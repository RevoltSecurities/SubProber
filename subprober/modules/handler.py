import asyncio
from colorama import Fore, Style
import sys
import os
import random
import aiofiles

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

try:
    from .cli.cli import __cli__
    from .banner.banner import __banner__
    from .config.config import __getconfig__
    from .extender.extender import __extender__
    from .help.help import __help__
    from .update.update import __updatelog__, __getzip__, __launch__
    from .version.version import __version__
    from .verify.verify import __getverify__
    from .core.core import __core__
except ImportError as e:
    print(f"[{bold}{red}INFO{reset}]: {bold}{white}Import Error occured in Module imports due to: {e}{reset}")
    print(f"[{bold}{blue}INFO{reset}]: {bold}{white}If you are encountering this issue more than a time please report the issues in Subprober Github page.. {reset}")
    exit()
    
    
args = __cli__()
configpath = __getconfig__()
banner = __banner__()


def version():
    try:
        latest = __version__()
        currentversion = "v2.0.0"
        
        if latest and  latest == currentversion:
            print(f"[{blue}{bold}Version{reset}]:{bold}{white}Subprober current version {currentversion} ({green}latest{reset}{bold}{white}){reset}", file=sys.stderr)
        elif latest and latest != currentversion:
            print(f"[{blue}{bold}Version{reset}]: {bold}{white}Subprober current version {currentversion} ({red}outdated{reset}{bold}{white}){reset}", file=sys.stderr)
        else:
            print(f"[{bold}{red}WRN{reset}]: {bold}{white}Unable to detect the version right now, please try again", file=sys.stderr)
            
    except Exception as e:
        if args.secret_debug:
            print(f"Exeption in handler version: {e}, {type(e)}")
        
def __update_handler__():
    try:
        if args.show_updates:
            __updatelog__(configpath)
            quit()
        current = "v2.0.0"
        pypi = "2.0.0"
        git = __version__()
        
        if current and current == git:
            
            print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober is already in latest version{reset}")
            
        elif current and current!= git:
            zipurl = __getzip__()
            if not zipurl:
                print(f"[{bold}{red}ALERT{reset}]: {bold}{white}Update Failed for Subprober, Please try to update the Subprober manually {reset}")
                quit()
            __launch__(zipurl, configpath)
            
            lat_pkg = __getverify__("subprober")
            if not lat_pkg:
                print(f"[{bold}{red}ALERT{reset}]: {bold}{white}Update Failed for Subprober, Please try to update the Subprober manually {reset}")
                quit()
            
            if lat_pkg == pypi:
                print(f"[{bold}{red}ALERT{reset}]: {bold}{white}Update Failed for Subprober, Please try to update the Subprober manually{reset}")
                quit()
                
            print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Verified the update for Subprober from {current} --> {git}{reset}")
            __updatelog__(configpath)
            quit()
        else:
            print(f"[{bold}{red}WRN{reset}]: {bold}{white}Unable to update now due to failed to get current version, please try again", file=sys.stderr)
            
    except Exception as e:
        if args.secret_debug:
            print(f"Exception in handler update: {e}, {type(e)}")
        
       
async def __urls__():
    try:
        url_list = []
        if args.url:
            url = args.url
                
            path =f"/{args.path}" if args.path else ""

            if url.startswith("https://") or url.startswith("http://"):
                    
                url = f"{url}/{path}"
           
                url_list.append(url)
             
            elif not  url.startswith("https://") or url.startswith("http://"):
                
                new_url = f"https://{url}{path}"
                url_list.append(new_url)
                
                if not args.disable_http_probe:
               
                    new_http = f"http://{url}{path}"
                    url_list.append(new_http)

            await __core__(args, url_list)
            
    except Exception as e:
        if args.secret_debug:
            print(f"Exception at urls: {e}, {type(e)}")
        
        
async def __files__():
    try:
        url_list = []
        async with aiofiles.open(args.filename, "r") as urls:
                            
            async for url in urls:
                                
                url = url.strip()
            
                path =f"/{args.path}" if args.path else ""
                        
                url = f"{url}{path}"
                        
                if url.startswith("https://") or url.startswith("http://") :
                                
                    url_list.append(url)
                            
                elif not  url.startswith("https://") or url.startswith("http://"):
                
                    new_url = f"https://{url}"
                    url_list.append(new_url)
                
                    if not args.disable_http_probe:
                        new_http = f"http://{url}"
                        url_list.append(new_http)
                        
        await __core__(args, url_list)
        
    except Exception as e:
        if args.secret_debug:
            print(f"exception in file: {e}, {type(e)}")
    
        
async def __sys__():
    try:
        
        url_list = []
        path =f"/{args.path}" if args.path else ""
        
        for url in sys.stdin:
            
            url = url.strip()
            
            path =f"/{args.path}" if args.path else ""
                        
            url = f"{url}{path}"
                        
            if url.startswith("https://") or url.startswith("http://") :
                                
                url_list.append(url)
                            
            elif not  url.startswith("https://") or url.startswith("http://"):
                
                new_url = f"https://{url}"
                url_list.append(new_url)
                
                if not args.disable_http_probe:
                    new_http = f"http://{url}"
                    url_list.append(new_http)
                    

        await __core__(args, url_list)
        
    except Exception as e:
        if args.secret_debug:
            print(f"Exception sys: {e}, {type(e)}")
            

async def __handler__():
    try:
        if not args.silent:
            print(f"{bold}{random_color}{banner}{reset}", file=sys.stderr)
            version()
        
        if args.help:
            __help__()
            
        if args.update or args.show_updates:
            __update_handler__()
            
        if args.url:
            await __urls__()
            
        if args.filename:
            await __files__()
            
        if sys.stdin.isatty():
            quit()
            
        await __sys__()

    except Exception as e:
        print(f"handler: {e}, {type(e)}")
            

def __source__():
    asyncio.run(__handler__())
            
            


    
    
    
    
    

    
