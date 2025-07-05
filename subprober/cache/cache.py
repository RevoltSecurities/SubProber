import asyncio
from typing import Any, AsyncIterator, Optional
from diskcache import Cache

class AsyncDiskCache:

    def __init__(self, directory: str):
        self._cache = Cache(directory,size_limit=0,eviction_policy='none')

    async def set(self, key: str, value: Any) -> None:
        await asyncio.to_thread(self._cache.set, key, value)

    async def get(self, key: str, default: Optional[Any] = None) -> Any:
        return await asyncio.to_thread(self._cache.get, key, default)

    async def add(self, key: str, value: Any) -> bool:
        return await asyncio.to_thread(self._cache.add, key, value)

    async def delete(self, key: str) -> None:
        await asyncio.to_thread(self._cache.delete, key)

    async def contains(self, key: str) -> bool:
        return await asyncio.to_thread(lambda: key in self._cache)

    async def clear(self) -> None:
        await asyncio.to_thread(self._cache.clear)

    async def close(self) -> None:
        await asyncio.to_thread(self._cache.close)

    async def iterkeys(self, reverse=False) -> AsyncIterator[str]:
        for key in self._cache.iterkeys():
            yield key

    async def size(self) -> int:
        return await asyncio.to_thread(lambda: len(self._cache))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
