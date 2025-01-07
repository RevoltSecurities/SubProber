from subprober.modules.logger.logger import logger
import asyncio
from playwright.async_api import async_playwright
from subprober.modules.utils.utils import Useragents
import os
import base64

class Headless:
    def __init__(
        self,
        args,
        ) -> None:
        
        self.args = args
        self.sandbox = True if os.geteuid() == 0 else False
        self.savepath = None
        self.chrome_options = []
    
    def setup(self) -> None:
        try:
            self.savepath = self.args.screenshot_path if self.args.screenshot_path else os.path.join(os.getcwd(),"screenshots")
            os.makedirs(self.savepath,exist_ok=True)
            
            if self.args.headless_options:
                self.chrome_options = self.args.headless_options.split(",")
        except Exception as e:
            if self.args.verbose:
                logger(f"Exception occured in the headless setup module due to: {e}, {type(e)}", "error", self.args.no_color)
                
    
    async def run(self, url: str, results: dict[str,str]) -> None:
        try:
            
            output = url.replace("://", "_").replace("/", "_")
            output_path = os.path.join(self.savepath,f"{output}.png") if not self.args.save_pdf else os.path.join(self.savepath,f"{output}.pdf")
            
            async with async_playwright() as playwright:
                
                headers = {"Upgrade-Insecure-Requests": "1"}
                
                launchers= {
                "headless": True,
                "timeout": self.args.screenshot_timeout*1000,
                "args": ["--ignore-certificate-errors",
                         "--disable-gpu",
                         "--disable-crash-reporter",
                         "--disable-notifications",
                         "--hide-scrollbars",
                         "--mute-audio"]+ self.chrome_options
                }
                
                if os.geteuid() == 0:
                    launchers["args"].extend(["--no-sandbox", "--disable-setuid-sandbox"])
                
                if self.args.screenshot_headers:
                    for header in self.screenshot_headers:
                        key,value = header.split(":",1)
                        headers[key.strip()] = value.strip()
                
                headers["User-Agent"] = Useragents() if self.args.random_agent else "git+Subprober/V2.XD"
                path = self.args.system_chrome_path if self.args.system_chrome_path else None
                
                if self.args.proxy:
                    launchers["proxy"] = {"server": self.args.proxy}
                
                browser = await playwright.chromium.launch(**launchers, chromium_sandbox=self.sandbox, executable_path=path)
                page = await browser.new_page(extra_http_headers=headers,ignore_https_errors=True)
                await page.goto(url)
                await asyncio.sleep(self.args.screenshot_idle)
                
                if self.args.save_pdf :
                    bytess = await page.pdf(path=output_path)
                else:
                    bytess = await page.screenshot(path=output_path, full_page=True)
                    
                if self.args.full_output or self.args.include_bytes and self.args.json:
                    results["HeadlessBody"] = base64.b64encode(bytess).decode()
                    
                if self.args.full_output or  self.args.json:
                    results["ScreenshotPath"] = output_path
                    
        except Exception as e:
            if self.args.verbose:
                logger(f"Exception occured in the headless run module due to: {e}, {type(e)}", "error", self.args.no_color)
        finally:
            await browser.close()