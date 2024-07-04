import os
import arsenic
import structlog
import aiofiles
import asyncio
import sys
import logging

structlog.configure(logger_factory=structlog.stdlib.LoggerFactory(),wrapper_class=structlog.stdlib.BoundLogger)
logging.basicConfig(stream=sys.stderr, level=logging.CRITICAL)
structlog.configure(
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    processors=[structlog.processors.JSONRenderer()],
    context_class=dict,
)

async def save(screenshot, args, url):
    try:
        
        if url.startswith("http://"):
            base = url.replace("http://", "http_")
        elif url.startswith("https://"):
            base = url.replace("https://", "https_")
        base_url = base.replace('/', '_')
        if args.output_directory:
            
            if os.path.isdir(args.output_directory):
                filename = f"{args.output_directory}/{base_url}.png"
            else:
                path = args.output_directory
                if not os.path.exists(path):
                    os.makedirs(path)
                    filename = f"{path}/{base_url}.png"
                else:
                    filename = f"{path}/{base_url}.png"
        else:
            pwd = os.getcwd()
            path = f"{pwd}/screenshot"
            if not os.path.exists(path):
                os.makedirs(path)
                filename = f"{path}/{base_url}.png"
            else:
                filename = f"{path}/{base_url}.png"
        async with aiofiles.open(filename, "wb") as streamw:
            await streamw.write(screenshot.read())
    except KeyboardInterrupt as e:
        SystemExit
    except asyncio.CancelledError as e:
        SystemExit
    except Exception as e:
        if args.secret_debug:
            print(f"Exception at st save: {e}, {type(e)}")

async def screenshots(args, url):
    try:
        
        if args.browser_type == "firefox":
            service = arsenic.services.Geckodriver(log_file=os.devnull)
            browser = arsenic.browsers.Firefox(**{'moz:firefoxOptions': {'args': ['-headless', '-private'], 'log': {'level': 'warn'}}})   
        else:
            service = arsenic.services.Chromedriver(log_file=os.devnull)
            browser = arsenic.browsers.Chrome()
            chrome_options = {'args': ['--headless', '--disable-gpu', '--no-sandbox',"--log-level=off","--silent", "--log-path=stderr"]}
            browser.capabilities = {'goog:chromeOptions': chrome_options}
        
        async with arsenic.get_session(service, browser) as session:
            await session.get(url, timeout=args.screenshot_timeout)
            await asyncio.sleep(0.000001)
            screenshot = await session.get_screenshot()
            await save(screenshot, args, url)
        
    except KeyboardInterrupt as e:
        SystemExit
    except asyncio.CancelledError as e:
        SystemExit
    
    except Exception as e:
        if args.secret_debug: #U may read and think but its for next devlopment so kept as secret and if you find something using this please report in subprober github page :)
            print(f"Exception at st module: {e}, {type(e)}")
        
        