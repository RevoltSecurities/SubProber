import asyncio
from typing import Any, Callable, Awaitable


class WorkerPool:
    """Bounded worker pool with multi-producer support.

    Architecture:
        Producers ──► [Bounded Queue] ──► N Workers ──► worker_func(item)
                       (backpressure)     (fixed, long-lived)

    - Fixed N long-lived worker coroutines pull items from a bounded queue
    - Multiple producers can submit() concurrently — all share the same queue
    - When queue is full, submit() blocks the calling producer (backpressure)
    - Rate limiter optionally applied per-item inside each worker
    - Graceful shutdown: drain queue → send N sentinels → gather workers

    Usage:
        pool = WorkerPool(num_workers=100, queue_size=200, worker_func=process)
        await pool.start()

        # Single producer
        for item in items:
            await pool.submit(item)

        # Or fan-out with multiple producers
        await pool.fan_out(host_iterator, url_generator, max_producers=8)

        await pool.shutdown()
    """

    def __init__(
        self,
        num_workers: int,
        queue_size: int,
        worker_func: Callable[[Any], Awaitable[None]],
        rate_limiter=None,
    ) -> None:
        self._num_workers = num_workers
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=queue_size)
        self._worker_func = worker_func
        self._rate_limiter = rate_limiter
        self._workers: list[asyncio.Task] = []
        self._started = False
        self._shutdown_complete = False

        self.completed_count = 0
        self.failed_count = 0

    async def _worker(self, _worker_id: int) -> None:
        """Long-lived worker coroutine. Pulls items from queue until sentinel."""
        while True:
            item = await self._queue.get()

            if item is None:
                self._queue.task_done()
                break

            try:
                if self._rate_limiter:
                    async with self._rate_limiter:
                        await self._worker_func(item)
                else:
                    await self._worker_func(item)
                self.completed_count += 1
            except Exception:
                self.failed_count += 1
            finally:
                self._queue.task_done()

    async def start(self) -> None:
        """Spawn worker coroutines."""
        if self._started:
            return
        self._started = True
        for i in range(self._num_workers):
            task = asyncio.create_task(self._worker(i))
            self._workers.append(task)

    async def submit(self, item: Any) -> None:
        """Submit an item to the pool. Blocks if queue is full (backpressure).

        Thread-safe for multiple concurrent producers — asyncio.Queue handles
        the coordination internally.
        """
        if not self._started:
            raise RuntimeError("WorkerPool not started — call start() first")
        if item is None:
            raise ValueError("None is reserved as a sentinel value")
        await self._queue.put(item)

    async def fan_out(
        self,
        items_iter,
        expand_func: Callable[[Any], Any],
        max_producers: int = 4,
        shutdown_event: asyncio.Event = None,
        on_item_done: Callable[[Any], Awaitable[None]] = None,
    ) -> None:
        """Fan-out pattern: multiple producer coroutines feed the worker pool.

        Instead of one sequential producer, spawns up to max_producers concurrent
        producers. Each producer takes an item from items_iter, expands it via
        expand_func into sub-items, and submits each sub-item to the pool.

        Args:
            items_iter: Async iterator of top-level items (e.g., hosts from HMap)
            expand_func: Async generator that expands an item into sub-items
                         (e.g., host → URLs via _targets_stream)
            max_producers: Number of concurrent producer coroutines
            shutdown_event: Optional event to signal early stop
            on_item_done: Optional async callback after all sub-items for an item
                          are submitted (e.g., delete host from HMap)
        """
        # Bounded channel for distributing top-level items to producers
        item_queue: asyncio.Queue = asyncio.Queue(maxsize=max_producers * 2)

        async def _producer(_id: int) -> None:
            """Single producer: pulls top-level items, expands, submits to pool."""
            while True:
                item = await item_queue.get()
                if item is None:
                    item_queue.task_done()
                    break

                try:
                    if shutdown_event and shutdown_event.is_set():
                        item_queue.task_done()
                        continue

                    async for sub_item in expand_func(item):
                        if shutdown_event and shutdown_event.is_set():
                            break
                        await self.submit(sub_item)

                    # Notify caller that all sub-items for this item are submitted
                    if on_item_done and not (shutdown_event and shutdown_event.is_set()):
                        await on_item_done(item)
                except Exception:
                    pass
                finally:
                    item_queue.task_done()

        # Spawn producers
        producers = []
        for i in range(max_producers):
            task = asyncio.create_task(_producer(i))
            producers.append(task)

        # Feed top-level items to producers (backpressure via item_queue)
        shutdown_triggered = False
        async for item in items_iter:
            if shutdown_event and shutdown_event.is_set():
                shutdown_triggered = True
                break
            await item_queue.put(item)

        if shutdown_triggered:
            # Cancel producers directly — sentinels can deadlock under backpressure
            # because producers may be blocked on self.submit() with a full worker queue
            for task in producers:
                if not task.done():
                    task.cancel()
        else:
            # Normal path: send sentinels so producers drain remaining items and exit
            for _ in producers:
                await item_queue.put(None)

        # Wait for all producers to finish (or be cancelled)
        await asyncio.gather(*producers, return_exceptions=True)

    async def shutdown(self) -> None:
        """Drain the queue, send sentinels, wait for all workers to finish."""
        if self._shutdown_complete:
            return

        # Wait for all submitted items to be processed
        await self._queue.join()

        # Send sentinel to each worker
        for _ in self._workers:
            await self._queue.put(None)

        # Wait for workers to exit
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._shutdown_complete = True

    async def cancel(self) -> None:
        """Cancel all workers immediately (for interrupt handling)."""
        for task in self._workers:
            if not task.done():
                task.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._shutdown_complete = True
