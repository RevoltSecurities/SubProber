import aiojarm
import asyncio
from revoltlogger import Logger
from typing import List, Tuple, Optional, Callable
from asyncio import Semaphore, Queue
from subprober.utils.utils import Utils

class JarmScanner:
    def __init__(
        self,
        max_concurrent: int = 50,
        timeout: int = 10,
        verbose: bool = False
    ):
        self.logger = Logger()
        self.verbose = verbose

        # Concurrency controls
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = Semaphore(self.max_concurrent)
        self.utils = Utils()
        # Results queue for streaming results
        self.results_queue = Queue()

    async def get_jarm_hash(self, url: str, port: int = 443) -> str:
        """Single JARM hash retrieval with semaphore control"""
        async with self.semaphore:
            try:
                domain = self.utils.GetDomain(url)

                # Add timeout to prevent hanging
                result = await asyncio.wait_for(
                    aiojarm.scan(domain, port),
                    timeout=self.timeout
                )
                return result[3] if result and len(result) > 3 else ""

            except asyncio.TimeoutError:
                if self.verbose:
                    self.logger.warn(f"Timeout scanning {url}:{port}")
                return ""
            except (KeyboardInterrupt, asyncio.CancelledError):
                raise
            except Exception as e:
                if self.verbose:
                    self.logger.warn(f"Exception for {url}: {e}")
                return ""

    async def scan_single(self, url: str, port: int = 443) -> Tuple[str, str, int]:
        """Scan single target and return tuple (url, hash, port)"""
        jarm_hash = await self.get_jarm_hash(url, port)
        return (url, jarm_hash, port)

    async def scan_batch(self, targets: List[Tuple[str, int]]) -> List[Tuple[str, str, int]]:
        """Scan multiple targets concurrently"""
        tasks = [
            asyncio.create_task(self.scan_single(url, port))
            for url, port in targets
        ]

        # Gather with return_exceptions to prevent one failure stopping all
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions and return valid results
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                if self.verbose:
                    url, port = targets[i]
                    self.logger.warn(f"Failed to scan {url}:{port} - {result}")
            else:
                valid_results.append(result)

        return valid_results

    async def scan_streaming(self, targets: List[Tuple[str, int]], callback: Optional[Callable] = None):
        """Scan targets and stream results as they complete"""
        tasks = [
            asyncio.create_task(self.scan_single(url, port))
            for url, port in targets
        ]

        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
                if callback:
                    await callback(result)
                else:
                    await self.results_queue.put(result)
            except Exception as e:
                if self.verbose:
                    self.logger.warn(f"Task failed: {e}")

    async def scan_with_chunks(self, targets: List[Tuple[str, int]], chunk_size: int = 100) -> List[Tuple[str, str, int]]:
        """Process targets in chunks to manage memory better"""
        all_results = []

        for i in range(0, len(targets), chunk_size):
            chunk = targets[i:i + chunk_size]
            if self.verbose:
                total_chunks = (len(targets) + chunk_size - 1) // chunk_size
                current_chunk = i // chunk_size + 1
                self.logger.info(f"Processing chunk {current_chunk}/{total_chunks}")

            chunk_results = await self.scan_batch(chunk)
            all_results.extend(chunk_results)

            # Small delay between chunks to prevent overwhelming resources
            await asyncio.sleep(0.1)

        return all_results

    async def scan_with_retries(self, url: str, port: int = 443, max_retries: int = 2) -> str:
        """Scan with exponential backoff retry logic"""
        for attempt in range(max_retries + 1):
            result = await self.get_jarm_hash(url, port)

            if result:  # Success
                return result

            if attempt < max_retries:
                wait_time = (2 ** attempt) * 0.5  # Exponential backoff
                await asyncio.sleep(wait_time)

        return ""

    def update_concurrency(self, new_limit: int):
        """Dynamically adjust concurrency limit"""
        self.max_concurrent = new_limit
        self.semaphore = Semaphore(new_limit)

    async def __aenter__(self):
        """Context manager support"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit"""
        # Wait for any remaining tasks
        await asyncio.sleep(0.1)
        return False


# Usage examples:
async def example_batch_scan():
    """Example: Batch scanning"""
    scanner = JarmScanner(
        max_concurrent=50,
        timeout=10,
        verbose=True
    )

    targets = [
        ("example.com", 443),
        ("google.com", 443),
        ("github.com", 443),
    ]

    results = await scanner.scan_batch(targets)

    for url, jarm_hash, port in results:
        print(f"{url}:{port} -> {jarm_hash}")


async def example_streaming_scan():
    """Example: Streaming results as they complete"""
    scanner = JarmScanner(
        max_concurrent=100,
        timeout=5,
        verbose=False
    )

    targets = [("example.com", 443), ("google.com", 443)]

    async def process_result(result):
        url, jarm_hash, port = result
        print(f"Completed: {url}:{port} -> {jarm_hash}")

    await scanner.scan_streaming(targets, callback=process_result)


async def example_chunked_scan():
    """Example: Process large lists in chunks"""
    scanner = JarmScanner(verbose=True)

    # Large target list
    targets = [(f"site{i}.com", 443) for i in range(1000)]

    # Process in chunks of 100
    results = await scanner.scan_with_chunks(targets, chunk_size=100)
    print(f"Scanned {len(results)} targets")


async def example_with_custom_utils():
    """Example: Use custom utils"""

    scanner = JarmScanner(
        max_concurrent=75,
        timeout=15,
        verbose=True
    )

    results = await scanner.scan_batch([("example.com", 443)])
    return results


async def example_context_manager():
    """Example: Using context manager"""
    async with JarmScanner(max_concurrent=50, verbose=True) as scanner:
        targets = [("example.com", 443), ("google.com", 443)]
        results = await scanner.scan_batch(targets)
        return results


# Run example
if __name__ == "__main__":
    asyncio.run(example_batch_scan())