from playwright.async_api import async_playwright
import asyncio
from subprober.logger.logger import Logger

logger = Logger()

async def check_browsers(verbose=False, colored=False) -> bool:
    try:
        async with async_playwright() as playwright:
            await playwright.chromium.launch()
            return True
    except Exception as e:
        if verbose:
            logger.warn(f"Browsers are not installed for Headless screenshots")
        return False
    
async def install_browsers(verbose, colored=False):
    try:
        process = await asyncio.create_subprocess_exec(
            'playwright', 'install','chromium'
        )

        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            logger("Browsers installed successfully")
            exit(0)  
        else:
            logger(f"Browsers installation failed, please try again manually with command: playwright install chromium")
            exit(1)
    except Exception as e:
        if verbose:
            logger(f"Exception occured in the browser installing module due to: {e}, {type(e)}")
        exit(1)