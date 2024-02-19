#!/usr/bin/python3
import asyncio
import aiohttp
from aiohttp.client_exceptions import ClientResponseError, ClientPayloadError, InvalidURL
import aiofiles
import os  
from colorama import Fore,Back,Style
import argparse
import requests
from bs4 import BeautifulSoup
import time as t
import warnings
import random
from alive_progress import alive_bar
import sys
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
from aiohttp import client_exceptions
requests.packages.urllib3.disable_warnings()
import platform
import resource
from bs4 import  XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning


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

colors = [ white, cyan, blue]

random_color = random.choice(colors)

url_list = []

results = []


async def help_me():
    
    print(f"""
          
{bold}{white}Subprober - An essential HTTP multi-purpose Probing Tool for Penetration testers

{bold}[{bold}{blue}Description{reset}{bold}{white}]{reset} :

    {bold}{white}Subprober is a high-performance tool designed for probing and  extract vital information efficiently.{reset}

{bold}[{bold}{blue}Options{reset}{bold}{white}]{reset}:{reset}{bold}{white}


    {bold}[{bold}{blue}INPUT{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -f,   --filename              Specify the filename containing a list of subdomains for targeted probing. 
                                      This flag is used to find and analyze status codes and other pertinent details.
                                      
        -u,   --url                   Specify a target URL for direct probing. This flag allows for the extraction of 
                                      status codes and other valuable information.
                                      
        stdin                         Subprober supports stdin input by using cat or echo command with subprober using pipe `|`
                                      
    {bold}[{bold}{blue}PROBES-CONFIG{reset}{bold}{white}]{reset}:{reset}{bold}{white}


        -tl,  --title                 Retrieve and display the title of subdomains.
 
        -sv,  --server                Identify and display the server information associated with subdomains.

        -wc,  --word-count            Retrieve and display the content length of subdomains.
        
        -l ,  --location              Display the redirected location of the response.

        -apt, --application-type      Determine and display the application type of subdomains.

        -p,   --path                  Specify a path for probe and get results ex:: -p admin.php
    
        -px,  --proxy                 Specify a proxy to send the requests through your proxy or BurpSuite ex: 127.0.0.1:8080
    
        -gw,  --grep-word             Enable The grep word flag will be usefull when grepping partiuclar codes like for 200: OK ---> cat subprober-results.txt | grep OK 
                                      This will show the results with 200-299 range codes
                                                                  
        -ar,  --allow-redirect        Enabling these flag will make Subprober to follow the redirection and ger results
        
        -dhp. --disable-http-probe    Disables the subprober from probing to http protocols and only for https when no protocol is specified
        
    {bold}[{bold}{blue}MATCHERS{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -ex,  --exclude               Exclude specific response status code(s) from the analysis.

        -mc,  --match                 Specify specific response status code(s) to include in the analysis.
                                      
    {bold}[{bold}{blue}OUTPUT{reset}{bold}{white}]{reset}:{reset}{bold}{white}
    
        -o,   --output                Define the output filename to store the results of the probing operation.
        
        -das, ---disable-auto-save    Disable the autosave of the results when no output file is specified 

    {bold}[{bold}{blue}Rate-Limits{reset}{bold}{white}]{reset}:{reset}{bold}{white}

                      
        -c,   --concurrency           Set the concurrency level for multiple processes. Default is 50.
        
        -to,  --timeout               Set a custom timeout value for sending requests.

        
    {bold}[{bold}{blue}UPDATES{reset}{bold}{white}]{reset}:{reset}{bold}{white}


        -up,  --update                Update Subprober to the latest version (pip required to be installed)

    {bold}[{bold}{blue}DEBUG{reset}{bold}{white}]{reset}:{reset}{bold}{white}

                      
        -h,   --help                  Show this help message for you and exit!
        
        -s,   --silent                Enable silent mode to suppress the display of Subprober banner and version information.

        -v,   --verbose               Enable verbose mode to display error results on the console.

        -nc,  --no-color              Enabling the --no-color will display the output without any CLI colors{reset}""")
    
    quit()




banner = f''' 

   _____       __    ____             __             
  / ___/__  __/ /_  / __ \_________  / /_  ___  _____
  \__ \/ / / / __ \/ /_/ / ___/ __ \/ __ \/ _ \/ ___/
 ___/ / /_/ / /_/ / ____/ /  / /_/ / /_/ /  __/ /    
/____/\__,_/_.___/_/   /_/   \____/_.___/\___/_/     
                                                         
                
                
                    {bold}{white}Author : D.Sanjai Kumar @CyberRevoltSecurities{reset}

                                                                         
                                                  '''
                                                  
parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("-f", "--filename",  type=str)

parser.add_argument("-h", "--help", action="store_true")

parser.add_argument("-u", "--url",  type=str )

parser.add_argument("-o", "--output", type=str)

parser.add_argument("-c", "--concurrency", type=int, default=50)

parser.add_argument("-tl", "--title", action="store_true")

parser.add_argument("-to", "--timeout", type=int, default=5)

parser.add_argument("-sv", "--server", action="store_true")

parser.add_argument("-l", "--location", action="store_true")

parser.add_argument("-wc", "--word-count",  action="store_true")

parser.add_argument("-apt", "--application-type",  action="store_true")

parser.add_argument("-ex", "--exclude",  type=str, nargs="*")

parser.add_argument("-mc", "--match",  type=str, nargs="*")

parser.add_argument("-s", "--silent", action="store_true")

parser.add_argument("-v", "--verbose", action="store_true")

parser.add_argument("-p", "--path", type=str)

parser.add_argument("-px", "--proxy", type=str)

parser.add_argument("-gw", "--grep-word", action="store_true")

parser.add_argument("-ar", "--allow-redirect", action="store_true")

parser.add_argument("-nc", "--no-color", action="store_true")

parser.add_argument("-up", "--update", action="store_true")

parser.add_argument("-das", "--disable-auto-save", action="store_true")

parser.add_argument("-dhp", "--disable-http-probe", action="store_true")




args = parser.parse_args()


async def get_version():
    
    
    version = "v1.0.7"
    
    url = f"https://api.github.com/repos/sanjai-AK47/Subprober/releases/latest"
    
    try:
            
                response =  requests.get(url, timeout=10)
        
                if response.status_code == 200:
            
                    
                    data = response.json()
                
                    latest = data.get('tag_name')
            
                    if latest == version:
                
                
                        print(f"[{blue}Version{reset}]: {bold}{white}Subprober current version {version} ({green}latest{reset})")
                
                
                    else:
                
                
                        print(f"[{blue}Version{reset}]: {bold}{white}Subprober current version {version} ({red}outdated{reset})")
                
                
                else:
            
                    pass
            
            
        
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        
        SystemExit
        
                
    except Exception as e:
        
        pass
        
        
async def limit_extender(): 
    
    try:
        
        soft , hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        
        new = 1000000
        
        osname = platform.system()
        
        if osname == "Linux" or  osname == "Darwin":
            
            resource.setrlimit(resource.RLIMIT_NOFILE, (new, hard))
            
    except KeyboardInterrupt as e:
        
        quit()
        
    except Exception as e:
        
        pass
            
            
        
async def save(url, args):
    
    try:
        
        
            if args.output:
        
        
            
                if os.path.isfile(args.output):
                
                    filename = args.output
                
                elif os.path.isdir(args.output):
                
                    filename = os.path.join(args.output, f"subprober_results.txt")
                
                else:
                
                    filename = args.output
                    
            else:
                if not args.disable_auto_save:
                
                    filename = "subprober_results.txt"
                
        
            async with aiofiles.open(filename, "a") as w:
                
                    await w.write(url + '\n')

    except KeyboardInterrupt as e:
        
        
        print(f"\n[{bold}{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        
        quit()
        
    except asyncio.CancelledError as e:
        
        
        SystemExit
        
        
        
    except Exception as e:
        
        pass
            
            
    
    
async def probe(url, args, session, sem, bar):
    
    
    try:
        
    
        async with sem:
            
        
            warnings.filterwarnings("ignore", category=ResourceWarning)
            
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            
            
            proxies = {
                "http": args.proxy,
                "https": args.proxy
            } if args.proxy else None
            
            timeout = args.timeout
            
            redirect = True if args.allow_redirect else False
            
            async with session.get(url, ssl=False, proxy=proxies, timeout=timeout, allow_redirects=redirect) as response:
                
                
                response_text = await response.content.read()
                
                server1 =  response.headers.get("server")
                
                server = server1 if server1 else "None"
        
                content_type = response.headers.get("Content-Type")
                
                rd = response.url if response.url else ""
                
                
        
                if content_type:
            
                        content_type = content_type.split(";")[0].strip()
            
            
                with warnings.catch_warnings():
                
                
                    warnings.filterwarnings("ignore", category=UserWarning)
                    
                    warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)
                    
                    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
                    
                    soup = BeautifulSoup(response_text, "html.parser",from_encoding="iso-8859-1")
                     
    
                    text = soup.get_text() 
                    
                    
                word_count = len(text.split())  
            
                title_tag = soup.title
                
                title = title_tag.string if title_tag else ""
                
                if not args.no_color:
                    
                    redirect = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{magenta}{rd}{reset}{bold}{white}]{reset} " if args.location else ""
                    
                else:
                    
                    redirect = f"[{rd}]" if args.location else ""
                
                
                if not args.no_color:
                    
                    server = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{magenta}{server}{reset}{bold}{white}]{reset} " if args.server else ""
                    
                else:
                    
                    server = f"[{server}]" if args.server else ""
                    
                if not args.no_color:
                    
                    content = f"{bold}{white}[{reset}{bold}{yellow}{content_type}{reset}{bold}{white}]{reset}" if args.application_type else ""
                    
                else:
                    
                    content = f"[{content_type}]" if args.application_type else ""
                    
                if not args.no_color:
                    
                    word =  f"{bold}{white}[{reset}{bold}{green}{word_count}{reset}{bold}{white}]{reset}" if args.word_count else ""
                    
                else:
                    
                    word =  f"[{word_count}]" if args.word_count else ""
                    
                if not args.no_color:
        
                    title = f"{bold}{white}[{reset}{bold}{cyan}{title}{reset}{bold}{white}]{reset}" if args.title else ""
                    
                else:
                    
                    title = f"[{title}]" if args.title else ""
                       
                
                if response.status >=200 and response.status <=299:
                    
                    if not args.no_color:
                    
                        status =f"{bold}{white}[{reset}{bold}{bold}{green}{response.status}{reset}{bold}{white}]{reset}"
                        
                    else:
                        
                        status =f"[{response.status}]"
                        
                    
                elif response.status >= 300 and response.status <=399:
                    
                    if not args.no_color:
                    
                        status =f"{bold}{white}[{reset}{bold}{bold}{yellow}{response.status}{reset}{bold}{white}]{reset}"
                        
                    else:
                        
                        status =f"[{response.status}]"
                    
                else:
                    
                    if not args.no_color:
                        
                        status =f"{bold}{white}[{reset}{bold}{red}{response.status}{reset}{bold}{white}]{reset}"
                        
                    else:
                        
                        status =f"[{response.status}]"
                        
                
                if response.status >=200 and response.status <=299:
                    
                    if args.grep_word:
                    
                        if not args.no_color:
                        
                            grep =f"{bold}{white}[{reset}{bold}{green}OK{reset}{bold}{white}]{reset}"
                        
                        else:
                        
                            grep =f"[OK]"
                        
                    
                elif response.status >= 300 and response.status <=399:
                    
                     if args.grep_word:
                    
                        if not args.no_color:
                        
                            grep =f"{bold}{white}[{reset}{bold}{cyan}RD{reset}{bold}{white}]{reset}"
                        
                        else:
                        
                            grep =f"[RD]"
                    
                else:
                    
                    if args.grep_word:
                    
                        if not args.no_color:
                        
                            grep =f"{bold}{white}[{reset}{bold}{red}ER{reset}{bold}{white}]{reset}"
                        
                        else:
                        
                            grep =f"[ER]" 
                            
                gword = grep if args.grep_word else ""
                
                        
                if not args.no_color:
                 
                    url = f"{bold}{white}{url}{reset}"
                    
                else:
                    
                    url = f"{url}"
                    
                
                
                if args.exclude and str(response.status) in args.exclude:
                
                    pass
                
                if not args.exclude  and not args.match:
                    
            
            
                        result = f"""{url} {gword}{status}{title}{server}{content}{word}{redirect}"""
                    
                        print(f"{result}\n")
                
                        await save(result, args)
                        
                if args.exclude  and not args.match:
                    
            
                    if str(response.status) not in args.exclude:
            
                        result = f"""{url} {gword}{status}{title}{server}{content}{word}{redirect}"""
                    
                        print(f"{result}\n")
                
                        await save(result, args)
                                    
                            
                if args.match and str(response.status) in args.match:
                
                        result = f"""{url} {gword}{status}{title}{server}{content}{word}"""
                        
                        print(f"{result}\n")
                        
                        await save(result, args)
                                           
                                           
                
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        
        SystemExit
        
    except aiohttp.ClientConnectionError as e:
        
        
        if args.verbose:
            
        
            print(f"[{bold}{red}INFO{reset}]: {bold}{white}Client Connection Exceeds for: {url}{reset}")
            
            
    except asyncio.TimeoutError as e:
        
         if args.verbose:
            
        
            print(f"[{bold}{red}INFO{reset}]: {bold}{white}Client Timeout Exceeds for: {url}{reset}")
            
    except asyncio.CancelledError as e:
        
        SystemExit
        
    except InvalidURL as e:
        
        pass
    
    except UnicodeError as e:
        
        pass
        
    except (ClientResponseError, ClientPayloadError) as e:
        
        if  not args.no_color:
            
            result = f"{bold}{white}{url}{reset} {bold}{white}[Invalid Response]{reset}"
            
        else:
            
            result = f"{url} [Invalid Response]"
            
        print(result)
        
        await save(result, args)
        
    except Exception as e:
        
        pass
    
        
    finally:
        
        bar()
    
    
    
async def concurrents():
    
    try:
        
        url_lists = list(set(url_list))
        
        sem = asyncio.Semaphore(args.concurrency)
        
        async with aiohttp.ClientSession() as session:
            
            with alive_bar(title=f"SubProber", total=len(url_lists), enrich_print=False) as bar:
                
                tasks = [probe(url, args, session, sem, bar) for url in url_lists]
                
                await asyncio.gather(*tasks,return_exceptions=False)
                
    except KeyboardInterrupt as e:
        
        print(f"\n[{bold}{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        SystemExit
        
    except asyncio.CancelledError as e:
                
        
        SystemExit
        
    except Exception as e:
        
        pass
    

    

async def all_sub():
    
    try:
        
        await limit_extender()
        
        if args.url and not args.filename:
            
            if not args.silent:
            
                print(f"{bold}{random_color}{banner}{reset}", file=sys.stderr)
            
                await get_version()
                
                
            if  args.url and args.output:

                print(f"[{green}INFO{reset}]: {bold}{white}Output will be saved in {args.output}{reset}")
            
            elif  args.url and not args.output:
                
                if not args.disable_auto_save:
        
                    print(f"[{green}INFO{reset}]: {bold}{white}Output will be saved in subprober_results.txt{reset}")
                
            
            
            if args.url and not args.filename:
            
            
                url = args.url
                
                path =f"/{args.path}" if args.path else ""

                if url.startswith("https://") or url.startswith("http://"):
                    
                    url = f"{url}/{path}"
           
                    url_list.append(url)
             
                elif not  url.startswith("https://") or url.startswith("http://"):
                
                   new_url = f"https://{url}{path}"
                   
                   if not args.disable_http_probe:
               
                        new_http = f"http://{url}{path}"
                   
                   url_list.append(new_url)
                   
                   if not args.disable_http_probe:
               
                        url_list.append(new_http)
                
                await concurrents()
        
        
        
        if args.filename and not args.url:
            
                if not args.silent:
                
                    print(f"{bold}{random_color}{banner}{reset}")
            
                    await get_version()
                    
                
                if   args.output:

                    print(f"[{green}INFO{reset}]: {bold}{white}Output will be saved in {args.output}{reset}")
            
                elif  not args.output:
                    
                    if not args.disable_auto_save:
        
        
                        print(f"[{green}INFO{reset}]: {bold}{white}Output will be saved in subprober_results.txt{reset}")
                    
                    
                if args.filename and not args.url:
                    
                    
                    try:
                    
                        filename = args.filename
                        
                        
                        
                        async with aiofiles.open(filename, "r") as urls:
                            
                            async for url in urls:
                                
                                url = url.strip()
            
                                path =f"/{args.path}" if args.path else ""
                        
                                url = f"{url}{path}"
                        
                                if url.startswith("https://") or url.startswith("http://") :
                                
                                    url_list.append(url)
                            
                                elif not  url.startswith("https://") or url.startswith("http://") :
                            
                                    new_url = f"https://{url}{path}"
                   
                                    if not args.disable_http_probe:
               
                                        new_http = f"http://{url}{path}"
                   
                                    url_list.append(new_url)
                   
                                    if not args.disable_http_probe:
               
                                        url_list.append(new_http)
                                
                        await concurrents()
                                
                                
                    except FileNotFoundError as e:
                    
                        print(f"[{red}INFO{reset}]: {bold}{white}{args.filename} not found. please check the file or file path exist or not!{reset}")
                        
                        quit()
                        
                    except Exception as e:
                        
                        pass
                    
                    
        if args.update:
            
                version = "v1.0.7"
    
                url = f"https://api.github.com/repos/sanjai-AK47/Subprober/releases/latest"
    
                try:
        
                    async with aiohttp.ClientSession() as req:
                        
                        async with req.get(url) as response:

                            if response.status == 200:
            
                                data = await response.json()
                            
                                latest = data.get('tag_name')
            
                                if latest == version:
                
                
                                    print(f"[{bold}{blue}Version{reset}]: {bold}{white}Subprober already in latest version dont worry :){reset}")
                
                        
                                    quit()
                
                                else:
                        
                                    try:
                            
                                        print(f"[{bold}{blue}UPDATE{reset}]: {bold}{white}Updating the Subprober{reset}")
                
                                        os.system("pip install git+https://github.com/sanjai-AK47/Subprober.git")
                            
                                        print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Please check whether Subprober updated to latest version or update it through manually{reset}")
                            
                                        quit()
                            
                            
                                    except Exception as e:
                            
                                        print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober update failed due to some error{reset}")
                            
                                        quit()
                
                            else:
            
                                print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober update failed due to some error{reset}")
                    
                                quit()
                    
                except KeyboardInterrupt as e:
        
                    print(f"[{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        
                    quit()
        
                except aiohttp.TimeoutError as e:
        
                    print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober update failed due to failed to reach Subprober Repository please report this issue{reset}")
        
                    quit()
                
                except Exception as e:
                
                    print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober update failed due to failed to reach Subprober Repository please report this issue{reset}")
       
                    quit()
                    
                    
        if args.help:
            
            print(f"{bold}{random_color}{banner}{reset}", file=sys.stderr)
            
            await help_me()
            
            
        if not args.filename and not args.url:
            
            try:
                
                if not args.silent:
                    
                    print(f"{bold}{random_color}{banner}{reset}")
            
                    
                    await get_version()
                    
                path =f"/{args.path}" if args.path else ""
                
                for line in sys.stdin:
                      
                      url = f"{line.strip()}{path}"
                      
                      if url.startswith("https://") or url.startswith("http://"):
                          
                        
                          
                          
                        url_list.append(url)
                        
                        
                      else:
                         
                          new_url = f"https://{url}{path}"
                   
                          if not args.disable_http_probe:
               
                            new_http = f"http://{url}{path}"
                   
                          url_list.append(new_url)
                   
                          if not args.disable_http_probe:
               
                            url_list.append(new_http)
                          
                await concurrents()
            
            except KeyboardInterrupt as e:
                
                
                   print(f"[{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
                   
                   
                   quit()
                   
                   
            except Exception as e:
                
                   pass
               
    except KeyboardInterrupt as e:
        
        
        print(f"[{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        
        SystemExit
        
        
    except asyncio.CancelledError as e:
        
        SystemExit
        
    except Exception as e:
        
        print(f"[{blue}INFO{reset}]:Unknow error occured due to : {e}, please report this issue in Subprober github page")
        
        quit()
        