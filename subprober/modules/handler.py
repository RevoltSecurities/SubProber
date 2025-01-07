import asyncio
from colorama import Fore, Style, init
import sys
import os
import random

init()

red =  Fore.RED
green = Fore.GREEN
magenta = Fore.MAGENTA
cyan = Fore.CYAN
mixed = Fore.RED + Fore.BLUE
blue = Fore.BLUE
yellow = Fore.YELLOW
white = Fore.WHITE
lm = Fore.LIGHTMAGENTA_EX
reset = Style.RESET_ALL
bold = Style.BRIGHT
colors = [ green, cyan, blue]
random_color = random.choice(colors)

from subprober.modules.cli.cli import cli
from subprober.modules.banner.banner import banner
from subprober.modules.config.config import configdir
from subprober.modules.extender.extender import extender
from subprober.modules.help.help import help
from subprober.modules.version.version import Gitversion
from subprober.modules.core.core import Subprober
from subprober.modules.logger.logger import logger, bannerlog
from subprober.modules.update.update import updatelog
from subprober.modules.utils.utils import *
from subprober.modules.validate.headless import check_browsers, install_browsers

extender()
args = cli()
configpath = configdir()
banner = banner()
git = "v3.0.1"

def version():
    try:
        latest = Gitversion()
        if latest and latest == git:
            print(f"[{blue}{bold}version{reset}]:{bold}{white}subprober current version {git} ({green}latest{reset}{bold}{white}){reset}", file=sys.stderr)
        elif latest and latest != git:
            print(f"[{blue}{bold}Version{reset}]: {bold}{white}subprober current version {git} ({red}outdated{reset}{bold}{white}){reset}", file=sys.stderr)
        else:
            logger(f"Unable to get the latest version of subprober", "warn", args.no_color)
    except (KeyboardInterrupt, asyncio.CancelledError):
        exit(1)
    except Exception as e:
        if args.verbose:
            logger(f"Exception occured in the version check module due to: {e}, {type(e)}", "warn", args.no_color)
        
async def Updates():
    try:
       if args.show_updates:
           updatelog()
           exit(0)
           
       if args.update:
            latest = Gitversion()
            if latest and latest == git:
                logger("Subprober is already in latest version", "info", args.no_color)
            else:
                logger(f"Downloading latest version of subprober", "info", args.no_color)
                
                process = await asyncio.create_subprocess_exec(
                "pip", "install", "-U", "git+https://github.com/RevoltSecurities/Subprober", "--break-system-packages",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode == 0:
                    logger("successfully updated subprober to latest version", "info", args.no_color)
                    updatelog()
                    exit(0)
                else:
                    logger("failed for updating latest version of subprober, try to update manually", "warn", args.no_color)
                    exit(1)
    except Exception as e:
        if args.secret_debug:
            print(f"Exception in handler update: {e}, {type(e)}")
            
async def start(urls) -> None:
    try:
        urls = validate_urls(urls,args.disable_http_probe)
        urls = add_ports_to_urls(urls, ports= string_to_str_list(args.port) if args.port else None)
        if args.path:
            path = await Reader(args.path,args) if os.path.isfile(args.path) else string_to_str_list(args.path)
        else:
            path = None
        
        urls = add_paths_to_urls(urls,path)
        
        subprober = Subprober(
            urls, 
            args, 
            hashes=string_to_str_list(args.hash), 
            mc=string_to_int_list(args.match_code),
            fc=string_to_int_list(args.filter_code),
            mcr=args.match_code_range,
            fcr=args.filter_code_range,
            ms=string_to_str_list(args.match_string),
            fs=string_to_str_list(args.filter_string),
            mrg=string_to_str_list(args.match_regex),
            frg=string_to_str_list(args.filter_regex),
            mpt=string_to_str_list(args.match_path),
            fpt=string_to_str_list(args.filter_path),
            ml=string_to_int_list(args.match_length),
            fl=string_to_int_list(args.filter_length),
            mlc=string_to_int_list(args.match_line_count),
            flc=string_to_int_list(args.filter_line_count), 
            mwc=string_to_int_list(args.match_word_count),
            fwc=string_to_int_list(args.filter_word_count),
            mrt=args.match_response_time,
            frt=args.filter_response_time                            
                                )
        await subprober.start()
        exit(0)
    except (KeyboardInterrupt, asyncio.CancelledError):
        exit(1)
    except Exception as e:
        logger(f"Exception occured in the handler start module due to: {e}, {type(e)}","warn", args.no_color)
        
async def handler():
    try:
        if args.help:
            bannerlog(banner)
            help()
            exit(0)
            
        if not args.silent:
            bannerlog(banner)
            version()
            
        if args.update or args.show_updates:
            await Updates()
            exit(0)
            
        if args.screenshot:
            browser = await check_browsers(args.verbose, args.no_color)
            if browser:
                if args.verbose:
                    logger(f"Browsers are already installed!", "verbose", args.no_color)
            if not browser:
                logger(f"Installing Browsers for Headless modes", "info", args.no_color)
                await install_browsers(args.verbose, args.no_color)
            
        if args.url:
            if args.output:
                await permissions(args.output, args)
            urls = string_to_str_list(args.url)
            await start(urls)
            exit(0)
        
        if args.filename:
            if args.output:
                await permissions(args.output, args)
            urls = await Reader(args.filename,args)
            if urls is None:
                if args.verbose:
                    logger(f"Error occured in the urls file reader due to no data found","error",args.no_color)
            await start(urls)
            exit(0)
        
        if sys.stdin.isatty():
            logger(f"no inputs provided for subprober", "warn", args.no_color)
            exit(1)
            
        else:
            if args.output:
                await permissions(args.output, args)
            urls = [domain.strip() for domain in sys.stdin if domain.strip()]
            await start(urls)
            exit(0)
    except (KeyboardInterrupt,asyncio.CancelledError):
        exit(1)
    except Exception as e:
        logger(f"Exception occured in the handler module due to: {e}, {type(e)}","warn",args.no_color) 

def Main():
    try:
        asyncio.run(handler())
    except (KeyboardInterrupt, asyncio.CancelledError):
        exit(1)