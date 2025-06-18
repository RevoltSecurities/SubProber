import asyncio
import os
import base64
from playwright.async_api import async_playwright
from utils.utils import Utils
from logger.logger import Logger

class Headless:
    def __init__(
        self,
        args,
    ) -> None:
        self.args = args
        self.logger = Logger()
        self.utils = Utils()
        self.sandbox = True if os.geteuid() == 0 else False
        self.savepath = None
        self.chrome_options = []
        self.screenshot_headers = {} 
        self._setup_configurations()

    def _setup_configurations(self) -> None:
    
        try:
            self.savepath = self.args.screenshot_path if self.args.screenshot_path else os.path.join(os.getcwd(), "screenshots")
            os.makedirs(self.savepath, exist_ok=True)

            if self.args.headless_options:
                self.chrome_options.extend(self.args.headless_options.split(","))

            if self.args.screenshot_headers:
                for header_str in self.args.screenshot_headers:
                    if ":" in header_str:
                        key, value = header_str.split(":", 1)
                        self.screenshot_headers[key.strip()] = value.strip()
                    else:
                        if self.args.verbose:
                            self.logger.warn(f"Warning: Invalid header format '{header_str}'. Expected 'Key:Value'.")
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occurred during Headless setup: {e}, {type(e)}")

    async def run(self, url: str, results: dict[str, str]) -> None:

        browser = None
        try:
            output_filename = url.replace("://", "_").replace("/", "_").replace("?", "_").replace("=", "_").replace("&", "_")
            output_extension = "pdf" if self.args.save_pdf else "png"
            output_path = os.path.join(self.savepath, f"{output_filename}.{output_extension}")

            async with async_playwright() as playwright:

                headers = {"Upgrade-Insecure-Requests": "1"}

                headers.update(self.screenshot_headers)

                headers["User-Agent"] = self.utils.Useragents() if self.args.random_agent else "git+Subprober/V2.XD"

                launch_args = {
                    "headless": True,
                    "timeout": self.args.screenshot_timeout * 1000,
                    "args": [
                        "--ignore-certificate-errors",
                        "--disable-gpu",
                        "--disable-crash-reporter",
                        "--disable-notifications",
                        "--hide-scrollbars",
                        "--mute-audio"
                    ] + self.chrome_options
                }

                if self.sandbox: 
                    launch_args["args"].extend(["--no-sandbox", "--disable-setuid-sandbox"])

                if self.args.proxy:
                    launch_args["proxy"] = {"server": self.args.proxy}

                browser = await playwright.chromium.launch(
                    **launch_args,
                    chromium_sandbox=self.sandbox,
                    executable_path=self.args.system_chrome_path if self.args.system_chrome_path else None
                )

                page = await browser.new_page(extra_http_headers=headers, ignore_https_errors=True)
                await page.goto(url)
                await asyncio.sleep(self.args.screenshot_idle)

                bytess = None
                if self.args.save_pdf:
                    bytess = await page.pdf(path=output_path)
                else:
                    bytess = await page.screenshot(path=output_path, full_page=True)

                if self.args.full_output or self.args.include_bytes and self.args.json:
                    if bytess: 
                        results["HeadlessBody"] = base64.b64encode(bytess).decode('utf-8')
                    else:
                        results["HeadlessBody"] = None
                if self.args.full_output or self.args.json:
                    results["ScreenshotPath"] = output_path

        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occurred in Headless.run for {url} due to: {e}, {type(e)}")
        finally:
            if browser:
                await browser.close()