import asyncio

class WaitGroups:
    """semaphore with WaitGroup semantics"""
    def __init__(self, value: int):
        self._sem = asyncio.Semaphore(value)
        self._value = value
        self._acquired = 0
        self._lock = asyncio.Lock()
        self._event = asyncio.Event()
        self._event.set()

    async def add(self):
        await self._sem.acquire()
        async with self._lock:
            self._acquired += 1
            self._event.clear()

    def done(self):
        self._sem.release()
        asyncio.create_task(self._decrement())

    async def _decrement(self):
        async with self._lock:
            self._acquired = max(0, self._acquired - 1)
            if self._acquired == 0:
                self._event.set()

    async def wait(self):
        """Wait until all acquired resources are released (acquired_count == 0)"""
        await self._event.wait()

    @property
    def acquired_count(self) -> int:
        return self._acquired