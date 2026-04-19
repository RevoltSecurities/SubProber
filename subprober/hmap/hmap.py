import asyncio
import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, AsyncGenerator


class HMap:
    """LevelDB-based async disk cache inspired by projectdiscovery/hmap.

    Wraps plyvel (synchronous LevelDB bindings) with asyncio using a
    dedicated ThreadPoolExecutor. Designed for high-throughput host
    deduplication with batch writes and chunked iteration.
    """

    def __init__(
        self,
        path: Optional[str] = None,
        write_buffer_size: int = 4 * 1024 * 1024,
        lru_cache_size: int = 8 * 1024 * 1024,
        bloom_filter_bits: int = 10,
        batch_size: int = 1000,
        max_workers: int = 4,
    ) -> None:
        import plyvel

        self._auto_cleanup = path is None
        self._path = path or tempfile.mkdtemp(prefix="subprober-hmap-")

        self._db = plyvel.DB(
            self._path,
            create_if_missing=True,
            write_buffer_size=write_buffer_size,
            lru_cache_size=lru_cache_size,
            bloom_filter_bits=bloom_filter_bits,
            max_open_files=512,
        )

        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="hmap-leveldb",
        )

        self._batch_size = batch_size
        self._batch = None
        self._batch_count = 0
        self._pending_keys: set[bytes] = set()
        self._batch_lock = asyncio.Lock()

        self._size = 0
        self._closed = False

    @property
    def path(self) -> str:
        """Return the LevelDB directory path."""
        return self._path

    def detach(self) -> None:
        """Prevent auto-cleanup of the LevelDB directory on close.

        Call this before close() when you want to persist the database
        for resume. After detach(), close() will flush and close the DB
        but leave the directory on disk.
        """
        self._auto_cleanup = False

    def _run(self, fn, *args):
        return asyncio.get_running_loop().run_in_executor(self._executor, fn, *args)

    async def add(self, key: str, value: bytes = b"1") -> bool:
        """Add a key if it doesn't exist. Returns True if new, False if duplicate."""
        key_bytes = key.encode("utf-8")

        def _add():
            if self._db.get(key_bytes) is not None:
                return False
            self._db.put(key_bytes, value)
            return True

        is_new = await self._run(_add)
        if is_new:
            self._size += 1
        return is_new

    def start_batch(self) -> None:
        """Begin a new write batch for bulk inserts."""
        self._batch = self._db.write_batch()
        self._batch_count = 0
        self._pending_keys.clear()

    async def batch_add(self, key: str, value: bytes = b"1") -> bool:
        """Add a key via batch write. Returns True if new.

        Deduplicates against both the DB and the current unflushed batch
        via an in-memory _pending_keys set.
        """
        key_bytes = key.encode("utf-8")

        async with self._batch_lock:
            if key_bytes in self._pending_keys:
                return False

            existing = await self._run(self._db.get, key_bytes)
            if existing is not None:
                return False

            self._batch.put(key_bytes, value)
            self._pending_keys.add(key_bytes)
            self._batch_count += 1
            self._size += 1

            if self._batch_count >= self._batch_size:
                await self._flush_batch_inner()

            return True

    async def flush_batch(self) -> None:
        """Flush the current write batch to disk."""
        async with self._batch_lock:
            await self._flush_batch_inner()

    async def _flush_batch_inner(self) -> None:
        """Internal flush — caller must hold _batch_lock."""
        if self._batch is not None and self._batch_count > 0:
            batch = self._batch
            await self._run(batch.write)
            self._batch = self._db.write_batch()
            self._batch_count = 0
            self._pending_keys.clear()

    async def get(self, key: str) -> Optional[bytes]:
        """Get a value by key. Returns None if not found."""
        key_bytes = key.encode("utf-8")
        return await self._run(self._db.get, key_bytes)

    async def delete(self, key: str) -> None:
        """Delete a key from the store."""
        key_bytes = key.encode("utf-8")

        def _delete():
            if self._db.get(key_bytes) is not None:
                self._db.delete(key_bytes)
                return True
            return False

        was_deleted = await self._run(_delete)
        if was_deleted:
            self._size = max(0, self._size - 1)

    async def contains(self, key: str) -> bool:
        """Check if a key exists."""
        key_bytes = key.encode("utf-8")
        result = await self._run(self._db.get, key_bytes)
        return result is not None

    async def size(self) -> int:
        """Return the number of entries. O(1) — tracked in memory."""
        return self._size

    async def rebuild_size(self) -> int:
        """Rebuild the in-memory _size counter by scanning LevelDB keys.

        Required when opening a persisted HMap where _size was lost.
        Key-only iteration is fast (sub-second for 1M keys) since
        LevelDB only reads index blocks, not value data.
        """
        def _count_keys():
            count = 0
            with self._db.iterator(include_value=False) as it:
                for _ in it:
                    count += 1
            return count

        self._size = await self._run(_count_keys)
        return self._size

    async def iterkeys(self) -> AsyncGenerator[str, None]:
        """Yield all keys via chunked iteration.

        Reads 10,000 keys at a time to avoid holding a LevelDB snapshot
        open across async yields while also not loading everything into memory.
        """
        chunk_size = 10000

        def _get_chunk(start_key=None):
            keys = []
            kwargs = {"include_value": False}
            if start_key is not None:
                kwargs["start"] = start_key
                kwargs["include_start"] = False
            with self._db.iterator(**kwargs) as it:
                for key in it:
                    keys.append(key)
                    if len(keys) >= chunk_size:
                        break
            return keys

        last_key = None
        while True:
            chunk = await self._run(_get_chunk, last_key)
            if not chunk:
                break
            for key in chunk:
                yield key.decode("utf-8")
            last_key = chunk[-1]
            if len(chunk) < chunk_size:
                break

    async def close(self) -> None:
        """Flush pending batch, close DB, clean up temp directory."""
        if self._closed:
            return
        self._closed = True

        if self._batch and self._batch_count > 0:
            try:
                await self.flush_batch()
            except Exception:
                pass

        def _close():
            self._db.close()

        try:
            await self._run(_close)
        except Exception:
            pass

        self._executor.shutdown(wait=True)

        if self._auto_cleanup and self._path and os.path.exists(self._path):
            shutil.rmtree(self._path, ignore_errors=True)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False
