import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

try:
    from websockets.asyncio.client import connect
    from websockets.exceptions import (
        WebSocketException,
        InvalidStatus,
        InvalidHandshake,
        InvalidURI
    )
except ImportError:
    # Fallback for older websockets versions
    from websockets import connect
    from websockets.exceptions import WebSocketException, InvalidHandshake, InvalidURI

    InvalidStatus = WebSocketException


@dataclass
class WebSocketResult:
    """Result object containing WebSocket connection information."""
    url: str
    status: str
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    error: Optional[str] = None
    response_time_ms: Optional[float] = None
    protocol: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'url': self.url,
            'status': self.status,
            'status_code': self.status_code,
            'headers': dict(self.headers) if self.headers else None,
            'error': self.error,
            'response_time_ms': self.response_time_ms,
            'protocol': self.protocol
        }


class AsyncWebSocketClient:
    """
    Asynchronous WebSocket client for probing WebSocket endpoints.

    This client uses the websockets library to test WebSocket connectivity
    and gather connection information. Concurrency control is handled by
    the caller.
    """

    def __init__(
            self,
            timeout: float = 5.0,
            max_size: int = 2 ** 20,
            verbose: bool = False
    ):
        """
        Initialize WebSocket client.

        Args:
            timeout: Connection timeout in seconds
            max_size: Maximum message size in bytes
            verbose: Enable verbose logging
        """
        self.timeout = timeout
        self.max_size = max_size
        self.verbose = verbose
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logger with appropriate level."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG if self.verbose else logging.WARNING)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def _convert_to_ws_url(self, url: str) -> Optional[str]:
        """
        Convert HTTP(S) URL to WS(S) URL.

        Args:
            url: HTTP or HTTPS URL

        Returns:
            WebSocket URL or None if invalid
        """
        url = url.strip()

        if url.startswith("https://"):
            return url.replace("https://", "wss://", 1)
        elif url.startswith("http://"):
            return url.replace("http://", "ws://", 1)
        elif url.startswith("wss://") or url.startswith("ws://"):
            return url
        else:
            self.logger.warning(
                f"Invalid URL scheme for '{url}'. Expected http(s):// or ws(s)://"
            )
            return None

    async def probe(self, url: str) -> WebSocketResult:
        """
        Probe a URL for WebSocket support with detailed response information.

        Args:
            url: HTTP(S) URL to probe

        Returns:
            WebSocketResult with connection details
        """
        start_time = asyncio.get_event_loop().time()

        # Convert URL
        ws_url = self._convert_to_ws_url(url)
        if not ws_url:
            return WebSocketResult(
                url=url,
                status='error',
                error='Invalid URL scheme'
            )

        try:
            # Use the connect context manager from websockets library
            async with connect(
                    ws_url,
                    open_timeout=self.timeout,
                    close_timeout=5,
                    ping_interval=20,
                    ping_timeout=10,
                    max_size=self.max_size,
            ) as websocket:
                response_time = (asyncio.get_event_loop().time() - start_time) * 1000

                # Extract connection information from the websocket connection
                headers = {}
                if hasattr(websocket, 'response') and websocket.response:
                    # Get headers from the handshake response
                    headers = dict(websocket.response.headers)

                # Get the negotiated subprotocol
                subprotocol = None
                if hasattr(websocket, 'protocol') and hasattr(websocket.protocol, 'subprotocol'):
                    subprotocol = websocket.protocol.subprotocol

                result = WebSocketResult(
                    url=url,
                    status='allowed',
                    status_code=101,  # WebSocket upgrade status
                    headers=headers,
                    response_time_ms=round(response_time, 2),
                    protocol=subprotocol
                )

                self.logger.info(f"WebSocket connection successful: {url} ({response_time:.2f}ms)")
                return result

        except asyncio.TimeoutError:
            self.logger.debug(f"Connection timeout for {url}")
            return WebSocketResult(
                url=url,
                status='disallowed',
                error='Connection timeout'
            )

        except InvalidStatus as e:
            # Extract status code from the exception if available
            status_code = None
            if hasattr(e, 'response') and hasattr(e.response, 'status_code'):
                status_code = e.response.status_code

            self.logger.debug(f"Invalid status for {url}: {e}")
            return WebSocketResult(
                url=url,
                status='disallowed',
                status_code=status_code,
                error=f'Invalid status: {str(e)}'
            )

        except InvalidHandshake as e:
            self.logger.debug(f"Invalid handshake for {url}: {e}")
            return WebSocketResult(
                url=url,
                status='disallowed',
                error=f'Invalid handshake: {str(e)}'
            )

        except InvalidURI as e:
            self.logger.debug(f"Invalid URI {url}: {e}")
            return WebSocketResult(
                url=url,
                status='error',
                error=f'Invalid URI: {str(e)}'
            )

        except (ConnectionRefusedError, OSError) as e:
            self.logger.debug(f"Connection refused for {url}: {e}")
            return WebSocketResult(
                url=url,
                status='disallowed',
                error=f'Connection refused: {type(e).__name__}'
            )

        except WebSocketException as e:
            self.logger.debug(f"WebSocket exception for {url}: {e}")
            return WebSocketResult(
                url=url,
                status='disallowed',
                error=f'WebSocket error: {str(e)}'
            )

        except (KeyboardInterrupt, asyncio.CancelledError):
            self.logger.info("Operation cancelled by user")
            raise

        except Exception as e:
            self.logger.warning(f"Unexpected error for {url}: {type(e).__name__} - {e}")
            return WebSocketResult(
                url=url,
                status='error',
                error=f'{type(e).__name__}: {str(e)}'
            )

    async def probe_multiple(self, urls: list[str]) -> list[WebSocketResult]:
        """
        Probe multiple URLs concurrently.

        Note: Concurrency control should be handled by the caller if needed.
        This method will execute all probes concurrently without limits.

        Args:
            urls: List of URLs to probe

        Returns:
            List of WebSocketResult objects
        """
        tasks = [self.probe(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=False)


# Usage example
async def main():
    client = AsyncWebSocketClient(
        timeout=5.0,
        verbose=True
    )

    # Single probe
    result = await client.probe("https://example.com")
    print(f"Status: {result.status}")
    print(f"Details: {result.to_dict()}")

    # Multiple probes
    urls = [
        "https://echo.websocket.org",
        "https://example.com",
        "https://invalid-websocket-url.com"
    ]
    results = await client.probe_multiple(urls)

    for result in results:
        print(f"\n{result.url}:")
        print(f"  Status: {result.status}")
        if result.status == 'allowed':
            print(f"  Response Time: {result.response_time_ms}ms")
            print(f"  Headers: {result.headers}")
        else:
            print(f"  Error: {result.error}")


if __name__ == "__main__":
    asyncio.run(main())