import aiodns
import asyncio
import socket
from typing import Optional, List
from contextlib import asynccontextmanager


class AsyncDnsClient:
    """
    Asynchronous DNS client for domain resolution.

    This client uses aiodns library to perform DNS queries with retry logic.
    Concurrency control is handled by the caller.
    """

    def __init__(
            self,
            nameservers: Optional[List[str]] = None,
            max_retries: int = 3,
            timeout: float = 5.0,
            verbose: bool = False
    ):
        """
        Initialize DNS client.

        Args:
            nameservers: List of DNS servers to use (default: Cloudflare and Google)
            max_retries: Maximum retry attempts per query
            timeout: Query timeout in seconds
            verbose: Enable verbose logging
        """
        self.nameservers = nameservers or ["1.1.1.1", "8.8.8.8"]
        self.max_retries = max_retries
        self.timeout = timeout
        self.verbose = verbose
        self._resolver = None
        self._resolver_lock = asyncio.Lock()

    def _log(self, message: str, level: str = "INFO"):
        """Log message if verbose is enabled."""
        if self.verbose:
            print(f"[DNS-{level}] {message}")

    async def _get_resolver(self) -> aiodns.DNSResolver:
        """
        Get or create a shared DNS resolver instance.

        Reuses a single resolver instance to avoid exhausting system inotify watches.
        Thread-safe through async lock.
        """
        if self._resolver is None:
            async with self._resolver_lock:
                # Double-check after acquiring lock
                if self._resolver is None:
                    try:
                        loop = asyncio.get_running_loop()
                        self._resolver = aiodns.DNSResolver(
                            loop=loop,
                            nameservers=self.nameservers,
                            rotate=True,
                            timeout=self.timeout
                        )
                        self._log(f"DNS resolver created with nameservers: {self.nameservers}")
                    except Exception as e:
                        self._log(f"Failed to create DNS resolver: {e}", "ERROR")
                        raise
        return self._resolver

    def _extract_domain(self, url: str) -> Optional[str]:
        """
        Extract domain from URL.

        Args:
            url: URL or domain string

        Returns:
            Cleaned domain name or None if invalid
        """
        if not url:
            return None

        # Remove protocol
        if "://" in url:
            url = url.split("://", 1)[1]

        # Remove path, query, fragment
        url = url.split("/", 1)[0].split("?", 1)[0].split("#", 1)[0]

        # Remove port
        url = url.split(":", 1)[0]

        # Remove trailing dot
        url = url.rstrip(".")

        return url.lower() if url else None

    async def _query_with_retry(
            self,
            domain: str,
            record_type: str,
            resolver: aiodns.DNSResolver
    ) -> List[str]:
        """
        Execute DNS query with retry logic.

        Args:
            domain: Domain to query
            record_type: DNS record type (A, AAAA, CNAME, etc.)
            resolver: DNS resolver instance

        Returns:
            List of resolved records
        """
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                self._log(f"Querying {domain} ({record_type}) - Attempt {attempt}/{self.max_retries}")

                results = await asyncio.wait_for(
                    resolver.query(domain, record_type),
                    timeout=self.timeout
                )

                # Parse results based on record type
                if record_type == 'CNAME':
                    records = [results.cname] if hasattr(results, 'cname') else []
                elif record_type in ('A', 'AAAA'):
                    records = [result.host for result in results] if results else []
                elif record_type == 'MX':
                    records = [result.host for result in results] if results else []
                elif record_type == 'TXT':
                    records = [result.text for result in results] if results else []
                elif record_type == 'NS':
                    records = [result.host for result in results] if results else []
                elif record_type == 'SOA':
                    if results:
                        soa = results
                        records = [f"{soa.nsname} {soa.hostmaster}"]
                    else:
                        records = []
                elif record_type == 'PTR':
                    records = [result.host for result in results] if results else []
                else:
                    records = []

                if records:
                    self._log(f"Successfully resolved {domain} ({record_type}): {records}")
                    return records
                else:
                    self._log(f"No records found for {domain} ({record_type})")
                    return []

            except asyncio.TimeoutError:
                last_exception = f"Timeout after {self.timeout}s"
                self._log(f"Timeout for {domain} ({record_type}) on attempt {attempt}", "WARN")

            except aiodns.error.DNSError as e:
                # DNS-specific errors (NXDOMAIN, SERVFAIL, etc.)
                if e.args[0] == aiodns.error.ARES_ENOTFOUND:
                    self._log(f"Domain not found: {domain}", "DEBUG")
                    return []  # No retry for NXDOMAIN
                elif e.args[0] == aiodns.error.ARES_ENODATA:
                    self._log(f"No data for {domain} ({record_type})", "DEBUG")
                    return []  # No retry for NODATA
                last_exception = f"DNS error: {e}"
                self._log(f"DNS error for {domain} ({record_type}): {e}", "WARN")

            except socket.gaierror as e:
                last_exception = f"Socket error: {e}"
                self._log(f"Socket error for {domain} ({record_type}): {e}", "WARN")

            except (KeyboardInterrupt, asyncio.CancelledError):
                self._log("Query cancelled by user", "INFO")
                raise

            except Exception as e:
                last_exception = f"Unexpected error: {e}"
                self._log(f"Unexpected error for {domain} ({record_type}): {e}", "ERROR")

            # Exponential backoff between retries
            if attempt < self.max_retries:
                backoff = min(2 ** (attempt - 1), 5)  # Max 5 seconds
                self._log(f"Retrying in {backoff}s...", "DEBUG")
                await asyncio.sleep(backoff)

        # All retries exhausted
        self._log(f"All retries exhausted for {domain} ({record_type}). Last error: {last_exception}", "ERROR")
        return []

    async def resolve(
            self,
            url: str,
            record_type: str = 'A'
    ) -> List[str]:
        """
        Resolve domain with automatic retry and resource management.

        Args:
            url: URL or domain to resolve
            record_type: DNS record type (A, AAAA, CNAME, MX, TXT, NS, SOA, PTR)

        Returns:
            List of resolved records
        """
        domain = self._extract_domain(url)

        if not domain:
            self._log(f"Invalid domain: {url}", "ERROR")
            return []

        try:
            # Get shared resolver instance
            resolver = await self._get_resolver()
            return await self._query_with_retry(domain, record_type, resolver)
        except (KeyboardInterrupt, asyncio.CancelledError):
            return []
        except Exception as e:
            self._log(f"Fatal error resolving {domain}: {e}", "ERROR")
            return []

    async def resolve_many(
            self,
            domains: List[str],
            record_type: str = 'A'
    ) -> dict[str, List[str]]:
        """
        Resolve multiple domains concurrently.

        Note: Concurrency control should be handled by the caller if needed.
        This method will execute all queries concurrently without limits.

        Args:
            domains: List of URLs/domains to resolve
            record_type: DNS record type

        Returns:
            Dictionary mapping domain to resolved records
        """
        tasks = [self.resolve(domain, record_type) for domain in domains]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            domain: result if isinstance(result, list) else []
            for domain, result in zip(domains, results)
        }

    async def close(self):
        """
        Clean up DNS resolver resources.

        Should be called when done with the client to properly release resources.
        """
        self._log("Closing DNS client", "INFO")
        self._resolver = None

    async def resolve_with_fallback(
            self,
            url: str,
            record_types: List[str] = None
    ) -> dict[str, List[str]]:
        """
        Resolve domain with multiple record types as fallback.

        Args:
            url: URL or domain to resolve
            record_types: List of record types to try (default: A, AAAA)

        Returns:
            Dictionary mapping record type to resolved records
        """
        if record_types is None:
            record_types = ['A', 'AAAA']

        results = {}
        for record_type in record_types:
            records = await self.resolve(url, record_type)
            if records:
                results[record_type] = records

        return results


async def main():
    # Initialize DNS client
    dns_client = AsyncDnsClient(
        nameservers=["1.1.1.1", "8.8.8.8"],
        max_retries=3,
        timeout=5.0,
        verbose=True
    )

    # Single resolution
    print("=== Single Resolution ===")
    results = await dns_client.resolve("example.com", "A")
    print(f"A records for example.com: {results}\n")

    # Multiple resolutions
    print("=== Multiple Resolutions ===")
    domains = ["google.com", "github.com", "cloudflare.com"]
    results = await dns_client.resolve_many(domains, "A")
    for domain, ips in results.items():
        print(f"{domain}: {ips}")

    # Resolution with fallback
    print("\n=== Resolution with Fallback ===")
    fallback_results = await dns_client.resolve_with_fallback("google.com", ["A", "AAAA"])
    for record_type, records in fallback_results.items():
        print(f"{record_type}: {records}")

    # Different record types
    print("\n=== Different Record Types ===")
    mx_records = await dns_client.resolve("gmail.com", "MX")
    print(f"MX records for gmail.com: {mx_records}")

    ns_records = await dns_client.resolve("google.com", "NS")
    print(f"NS records for google.com: {ns_records}")


if __name__ == "__main__":
    asyncio.run(main())