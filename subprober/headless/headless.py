import asyncio
import os
import base64
import shutil
from tempfile import mkdtemp
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from revoltlogger import Logger
from revoltutils.httputils import UserAgent


class Headless:
    """
    Efficient headless browser manager for capturing webpage screenshots.

    Features:
    - Single persistent browser instance with on-demand page creation
    - Pages created and destroyed per request (no pooling)
    - Automatic sandbox detection for Linux root environments
    - Support for custom headers, proxy, and Chrome options
    - Concurrent screenshot capture with results containing only available data
    """

    def __init__(
            self,
            headless: bool = True,
            timeout: int = 30,
            screenshot_path: Optional[str] = None,
            save_pdf: bool = False,
            full_page: bool = True,
            idle_time: float = 0,
            chrome_options: Optional[List[str]] = None,
            headers: Optional[Dict[str, str]] = None,
            proxy: Optional[str] = None,
            system_chrome_path: Optional[str] = None,
            random_agent: bool = False,
            include_bytes: bool = False,
            verbose: bool = False
    ):
        """
        Initialize Headless browser manager.

        Args:
            headless: Run browser in headless mode
            timeout: Navigation timeout in seconds
            screenshot_path: Directory to save screenshots
            save_pdf: Save as PDF instead of PNG
            full_page: Capture full page screenshot
            idle_time: Wait time after page load (idle time)
            chrome_options: Additional Chrome launch options
            headers: Custom HTTP headers
            proxy: Proxy server URL
            system_chrome_path: Path to system Chrome executable
            random_agent: Use random user agent
            include_bytes: Include base64 bytes in results
            verbose: Enable verbose logging
        """
        self.headless = headless
        self.timeout = timeout * 1000  # Convert to milliseconds
        self.save_pdf = save_pdf
        self.full_page = full_page
        self.idle_time = idle_time
        self.chrome_options = chrome_options or []
        self.headers = headers or {}
        self.proxy = proxy
        self.system_chrome_path = system_chrome_path
        self.random_agent = random_agent
        self.include_bytes = include_bytes
        self.verbose = verbose

        # Logger
        self.logger = Logger()

        # Setup save path
        self.savepath = screenshot_path or os.path.join(os.getcwd(), "screenshots")
        os.makedirs(self.savepath, exist_ok=True)

        # Browser management - single persistent instance
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.user_data_dir: str = mkdtemp(prefix="subprober-headless-")

        # Initialization control
        self.init_lock = asyncio.Lock()
        self.initialized = False
        self.closed = False

        # Detect sandbox requirement
        self.must_disable_sandbox = self._must_disable_sandbox()

    @staticmethod
    def _must_disable_sandbox() -> bool:
        """
        Determine if sandbox must be disabled.
        Linux with root user needs "--no-sandbox" option.

        Returns:
            True if running as root on Linux, False otherwise
        """
        try:
            import platform
            return platform.system() == "Linux" and os.geteuid() == 0
        except (AttributeError, ImportError):
            return False

    @staticmethod
    async def check_browsers(verbose: bool = False) -> bool:
        """
        Check if Playwright browsers are installed.

        Args:
            verbose: Enable verbose logging

        Returns:
            True if browsers are installed, False otherwise
        """
        logger = Logger()
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch()
                await browser.close()
                return True
        except Exception as e:
            if verbose:
                logger.warn(f"Browsers not installed: {e}")
            return False

    @staticmethod
    async def install_browsers(verbose: bool = False) -> bool:
        """
        Install Playwright browsers.

        Args:
            verbose: Enable verbose logging

        Returns:
            True if installation successful, False otherwise
        """
        logger = Logger()
        try:
            process = await asyncio.create_subprocess_exec(
                'playwright', 'install', 'chromium',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                if verbose:
                    logger.info("Browsers installed successfully")
                return True
            else:
                logger.error(
                    "Browser installation failed. "
                    "Please run: playwright install chromium"
                )
                return False
        except Exception as e:
            if verbose:
                logger.error(f"Browser installation error: {e}")
            return False

    def _safe_filename(self, url: str) -> str:
        """
        Generate safe filename from URL.

        Args:
            url: URL to convert to filename

        Returns:
            Safe filename string truncated to 200 characters
        """
        safe_url = (url.replace("://", "_")
                    .replace("/", "_")
                    .replace("?", "_")
                    .replace("=", "_")
                    .replace("&", "_")
                    .replace(":", "_")
                    .replace(".", "_"))
        return safe_url[:200]

    async def _init_browser(self) -> None:
        """
        Initialize the browser instance with context.
        Thread-safe initialization with lock.
        """
        if self.initialized or self.closed:
            return

        async with self.init_lock:
            if self.initialized or self.closed:
                return

            if self.verbose:
                self.logger.info("Initializing browser instance...")

            try:
                self.playwright = await async_playwright().start()

                launch_args = [
                    "--ignore-certificate-errors",
                    "--disable-gpu",
                    "--disable-crash-reporter",
                    "--disable-notifications",
                    "--hide-scrollbars",
                    "--mute-audio",
                    "--window-size=1280,720",
                    "--incognito",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-background-timer-throttling",
                    "--disable-backgrounding-occluded-windows",
                    "--disable-renderer-backgrounding",
                ]

                # Add custom chrome options
                launch_args.extend(self.chrome_options)

                # Disable sandbox if needed
                if self.must_disable_sandbox:
                    launch_args.extend(["--no-sandbox", "--disable-setuid-sandbox"])
                    if self.verbose:
                        self.logger.info("Sandbox disabled (running as root)")

                launch_options = {
                    "headless": self.headless,
                    "args": launch_args,
                }

                # Set proxy if provided
                if self.proxy:
                    launch_options["proxy"] = {"server": self.proxy}

                # Use system chrome if path provided
                if self.system_chrome_path:
                    launch_options["executable_path"] = self.system_chrome_path

                # Launch browser
                self.browser = await self.playwright.chromium.launch(**launch_options)

                # Create persistent context
                context_options = {
                    "viewport": {"width": 1280, "height": 720},
                    "ignore_https_errors": True,
                    "user_agent": "git+Subprober/V2.XD",
                }

                if self.proxy:
                    context_options["proxy"] = {"server": self.proxy}

                self.context = await self.browser.new_context(**context_options)

                self.initialized = True

                if self.verbose:
                    self.logger.info("Browser initialized successfully")

            except Exception as e:
                self.logger.error(f"Failed to launch browser: {e}")
                await self._cleanup_on_error()
                raise

    async def _cleanup_on_error(self):
        """Cleanup resources on initialization error."""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass
        finally:
            self.context = None
            self.browser = None
            self.playwright = None

    async def capture(self, url: str, **options) -> List[Dict]:
        """
        Capture screenshot by creating a new page.
        Each request: create page -> navigate -> screenshot -> close page.

        Args:
            url: URL to capture
            **options: Additional options (reserved for future use)

        Returns:
            List containing single result dictionary with only available data.
            Always includes 'url' and 'status'. Other fields included only if available:
            - screenshot_path: Path to saved screenshot file
            - screenshot_bytes: Base64 encoded bytes (if include_bytes=True)
            - file_size: Size of screenshot file in bytes
            - file_format: Format of screenshot (png or pdf)
            - viewport_width: Browser viewport width
            - viewport_height: Browser viewport height
            - final_url: Final URL after redirects
            - http_status: HTTP response status code
            - load_time_ms: Time taken to load and capture in milliseconds
            - screenshot_dimensions: Dimensions as "widthxheight" (PNG only)
            - content_type: Content-Type header from response
        """
        # Ensure browser is initialized
        if not self.initialized:
            await self._init_browser()

        if self.closed:
            raise RuntimeError("Browser has been closed")

        results = {
            "url": url,
            "status": "failed"
        }

        page: Optional[Page] = None
        start_time = asyncio.get_event_loop().time()

        try:
            page = await self.context.new_page()

            current_headers = {}
            if self.random_agent:
                current_headers["User-Agent"] = UserAgent()
            else:
                current_headers["User-Agent"] = "git+Subprober/V2.XD"
            current_headers.update(self.headers)

            await page.set_extra_http_headers(current_headers)

            page.set_default_navigation_timeout(self.timeout)
            page.set_default_timeout(self.timeout)

            if self.verbose:
                self.logger.info(f"Capturing: {url}")

            response = await page.goto(
                url,
                timeout=self.timeout,
                wait_until="domcontentloaded"
            )

            try:
                await page.wait_for_load_state("load", timeout=5000)
            except Exception:
                pass

            if self.idle_time > 0:
                try:
                    await page.wait_for_load_state("networkidle", timeout=int(self.idle_time * 1000))
                except Exception:
                    await asyncio.sleep(self.idle_time)

            final_url = page.url
            viewport = page.viewport_size

            if response:
                results["http_status"] = response.status
                if response.headers:
                    content_type = response.headers.get('content-type')
                    if content_type:
                        results["content_type"] = content_type

            output_filename = self._safe_filename(url)
            output_extension = "pdf" if self.save_pdf else "png"
            output_path = os.path.join(
                self.savepath,
                f"{output_filename}.{output_extension}"
            )

            screenshot_bytes = None

            if self.save_pdf:
                screenshot_bytes = await page.pdf(
                    path=output_path,
                    format='A4',
                    print_background=True
                )
            else:
                screenshot_bytes = await page.screenshot(
                    path=output_path,
                    full_page=self.full_page
                )

                # Parse PNG dimensions
                try:
                    import struct
                    if screenshot_bytes and len(screenshot_bytes) > 24:
                        width, height = struct.unpack('>LL', screenshot_bytes[16:24])
                        results["screenshot_dimensions"] = f"{width}x{height}"
                except Exception:
                    pass

            if os.path.exists(output_path):
                results["file_size"] = os.path.getsize(output_path)

            load_time = (asyncio.get_event_loop().time() - start_time) * 1000

            results["status"] = "success"
            results["screenshot_path"] = output_path
            results["file_format"] = output_extension

            if viewport:
                if viewport.get('width'):
                    results["viewport_width"] = viewport['width']
                if viewport.get('height'):
                    results["viewport_height"] = viewport['height']

            results["final_url"] = final_url
            results["load_time_ms"] = round(load_time, 2)

            if self.include_bytes and screenshot_bytes:
                results["screenshot_bytes"] = base64.b64encode(screenshot_bytes).decode('utf-8')

            if self.verbose:
                file_size = results.get("file_size", 0)
                self.logger.info(
                    f"Success: {url} ({file_size} bytes, {load_time:.0f}ms)"
                )

        except asyncio.TimeoutError:
            if self.verbose:
                self.logger.warn(f"Timeout: {url}")
        except Exception as e:
            if self.verbose:
                self.logger.error(f"Failed {url}: {type(e).__name__} - {e}")
        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    if self.verbose:
                        self.logger.warn(f"Page close error for {url}: {e}")

        return [results]

    async def close(self):
        """
        Close browser and cleanup resources.
        Should be called when done with all screenshot operations.
        """
        if self.closed:
            return

        self.closed = True

        try:
            # Close context
            if self.context:
                try:
                    await self.context.close()
                except Exception as e:
                    if self.verbose:
                        self.logger.warn(f"Context close error: {e}")
                finally:
                    self.context = None

            # Close browser
            if self.browser:
                try:
                    await self.browser.close()
                except Exception as e:
                    if self.verbose:
                        self.logger.warn(f"Browser close error: {e}")
                finally:
                    self.browser = None

            # Stop playwright
            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception as e:
                    if self.verbose:
                        self.logger.warn(f"Playwright stop error: {e}")
                finally:
                    self.playwright = None

            # Remove temp directory
            if self.user_data_dir and os.path.exists(self.user_data_dir):
                try:
                    shutil.rmtree(self.user_data_dir, ignore_errors=True)
                except Exception:
                    pass

            if self.verbose:
                self.logger.info("Browser cleanup completed")

        except Exception as e:
            if self.verbose:
                self.logger.error(f"Cleanup error: {e}")


async def main():
    """
    Example usage demonstrating concurrent screenshot capture.
    """

    # Check and install browsers if needed
    if not await Headless.check_browsers(verbose=True):
        print("Installing browsers...")
        await Headless.install_browsers(verbose=True)

    # Create browser instance
    headless = Headless(
        headless=True,
        timeout=30,
        screenshot_path="./screenshots",
        save_pdf=False,
        full_page=True,
        idle_time=1.0,
        verbose=True
    )

    try:
        # Test URLs
        urls = [
            "https://example.com",
            "https://github.com",
            "https://stackoverflow.com",
            "https://python.org",
            "https://nodejs.org"
        ]

        # Concurrent captures with semaphore control
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent

        async def capture_with_limit(url: str):
            """Wrapper with concurrency control."""
            async with semaphore:
                result = await headless.capture(url)
                status = result[0]['status']
                load_time = result[0].get('load_time_ms', 0)
                print(f"✓ {url} - {status} ({load_time:.0f}ms)")
                return result

        # Execute all captures concurrently
        print(f"\nCapturing {len(urls)} screenshots...")
        results = await asyncio.gather(
            *[capture_with_limit(url) for url in urls],
            return_exceptions=True
        )

        # Summary
        successful = sum(1 for r in results if isinstance(r, list) and r[0]['status'] == 'success')
        print(f"\nCompleted: {successful}/{len(urls)} successful")

    finally:
        # Always close browser
        await headless.close()


if __name__ == "__main__":
    asyncio.run(main())