from revoltlogger import Logger
import time
import asyncio
from typing import Optional

class ProgressLogger:

    def __init__(self, logger: Logger, total: Optional[int], title: str = "Progress"):
        self.logger = logger
        self.total = total
        self.title = title
        self.current = 0
        self.start_time = time.time()
        self.last_log_time = 0
        self.log_interval = 5
        self._lock = asyncio.Lock()

    async def update(self):
        async with self._lock:
            self.current += 1
            current_time = time.time()
            if (current_time - self.last_log_time >= self.log_interval) or (
                    self.total is not None and self.current == self.total):
                elapsed = current_time - self.start_time
                rate = self.current / elapsed if elapsed > 0 else 0
                percentage = (self.current / self.total * 100) if self.total is not None and self.total > 0 else 0
                if self.total is not None:
                    progress_msg = f"{self.title} |{'█' * int(percentage // 5)}{'░' * (20 - int(percentage // 5))}| {self.current}/{self.total} [{percentage:.1f}%] in {elapsed:.1f}s ({rate:.2f}/s)"
                else:
                    progress_msg = f"{self.title} | {self.current} processed in {elapsed:.1f}s ({rate:.2f}/s)"
                self.logger.info(progress_msg)
                self.last_log_time = current_time