import asyncio
import os
import base64
import shutil
from tempfile import mkdtemp
from typing import Optional, Dict, List
from playwright.async_api import async_playwright, Browser, Page
from subprober.utils.utils import Utils
from subprober.logger.logger import Logger

class Headless:
    def __init__(self, args) -> None:
        self.args = args
        self.logger = Logger()
        self.utils = Utils()
        self.sandbox = True if os.geteuid() == 0 else False
        self.savepath: Optional[str] = None
        self.chrome_options: List[str] = []
        self.page_headers: Dict[str, str] = {}
        self.browser: Optional[Browser] = None
        self.context = None
        self.playwright = None
        self.user_data_dir: str = mkdtemp(prefix="subprober-profile-")
        self.page_semaphore = asyncio.Semaphore(int(self.args.concurrency/2))
        self.timeout = int(self.args.screenshot_timeout * 1000)
        if self.args.screenshot:
            self._setup_configurations()


    def _setup_configurations(self) -> None:
        try:
            self.savepath = self.args.screenshot_path if self.args.screenshot_path else os.path.join(os.getcwd(), "screenshots")
            os.makedirs(self.savepath, exist_ok=True)

            if self.args.headless_options:
                self.chrome_options.extend(self.args.headless_options.split(","))

            if self.args.header:
                for header_str in self.args.header:
                    if ":" in header_str:
                        key, value = header_str.split(":", 1)
                        self.page_headers[key.strip()] = value.strip()
                    elif self.args.verbose:
                        self.logger.warn(f"Invalid header format '{header_str}', expected 'Key:Value'.")
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception during headless setup: {e}")

    async def _initialize_browser(self) -> None:
        if self.browser is None:
            self.playwright = await async_playwright().start()
            launch_args = {
                "headless": True,
                "timeout": (self.args.screenshot_timeout * 1000),
                "args": [
                    "--ignore-certificate-errors",
                    "--disable-gpu",
                    "--disable-crash-reporter",
                    "--disable-notifications",
                    "--hide-scrollbars",
                    "--mute-audio",
                    "--window-size=1280,800",
                    "--incognito",
                    "--disable-dev-shm-usage"
                ] + self.chrome_options,
                "proxy": {"server": self.args.proxy} if self.args.proxy else None,
            }

            if self.sandbox:
                launch_args["args"].extend(["--no-sandbox", "--disable-setuid-sandbox"])

            if self.args.headless_options:
                extra_args = [opt.strip() for opt in self.args.headless_options.split(",") if opt.strip()]
                launch_args["args"].extend(extra_args)

            executable_path = self.args.system_chrome_path if self.args.system_chrome_path else None

            try:
                self.browser = await self.playwright.chromium.launch(
                    **launch_args,
                    executable_path=executable_path,
                )
                # Single context of browser
                self.context = await self.browser.new_context()
            except Exception as e:
                self.logger.error(f"Failed to launch browser: {e}")
                raise

    async def close_browser(self) -> None:
        try:
            if self.playwright:
                await self.playwright.stop()
                
            if self.browser:
                await self.browser.close()

            if self.user_data_dir and os.path.exists(self.user_data_dir):
                shutil.rmtree(self.user_data_dir, ignore_errors=True)
        except Exception as e:
            self.logger.warn(f"Exception in Headless browser closing due to: {e}, {type(e)}")

    def _safe_filename(self, url: str) -> str:
        safe_url = url.replace("://", "_").replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_").replace(":", "_").replace(".", "_")
        return safe_url[:200]
    async def init_browser(self):
        await self._initialize_browser()

    async def run(self, url: str, results: Dict[str, str]) -> None:
        page: Optional[Page] = None
        try:
                await self.page_semaphore.acquire()
                if not self.browser or not self.context:
                    self.logger.info(f"Browser not initialized for {url}. Skipping.")
                    return

                output_filename = self._safe_filename(url)
                output_extension = "pdf" if self.args.save_pdf else "png"
                output_path = os.path.join(self.savepath, f"{output_filename}.{output_extension}")

                current_headers = {}
                if  self.args.random_agent:
                    current_headers["User-Agent"] = self.utils.Useragents()
                else:
                    current_headers["User-Agent"] = "git+Subprober/V2.XD"
                current_headers.update(self.page_headers)
                page = await self.context.new_page()
                await page.set_extra_http_headers(current_headers)
                page.set_default_navigation_timeout(self.timeout)

                await page.goto(url, timeout=self.timeout)

                if self.args.screenshot_idle > 0:
                    await asyncio.sleep(self.args.screenshot_idle)

                screenshot_bytes = None
                if  self.args.save_pdf:
                    screenshot_bytes = await page.pdf(path=output_path)
                else:
                    screenshot_bytes = await page.screenshot(
                            path=output_path,
                            full_page=not self.args.no_full_page
                    )

                if self.args.full_output or self.args.include_bytes and self.args.json:
                    if screenshot_bytes:
                        results["HeadlessBody"] = base64.b64encode(screenshot_bytes).decode('utf-8')
                    else:
                        results["HeadlessBody"] = ""
                if self.args.full_output or self.args.json:
                    results["ScreenshotPath"] = output_path
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception in Headless.run for {url}: {e} ({type(e).__name__})")
        finally:
            if page:
                try:
                    await page.close()
                except Exception:
                    pass
            self.page_semaphore.release()
