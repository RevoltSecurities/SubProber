#!/usr/bin/python3
import asyncio
import aiohttp
from aiohttp.client_exceptions import ClientResponseError, ClientPayloadError, InvalidURL
import aiofiles
import os  
from colorama import Fore,Style
import requests
from bs4 import BeautifulSoup
import time as t
import warnings
import random
from alive_progress import alive_bar
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import urllib3
from aiohttp import client_exceptions
requests.packages.urllib3.disable_warnings()
from bs4 import  XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
import uvloop
from .screenshot.screenshot import *
from .probes.probes import __getcname__, __getip__
from fake_useragent import UserAgent

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
    
    
async def __probe__(url, args, sem, bar, loop):
    
    try:
            
            warnings.filterwarnings("ignore", category=ResourceWarning)
            
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            
            headers={}
            
            timeout = args.timeout
            
            redirect = True if args.allow_redirect else False
            
            if args.header:
                for header in args.header:
                    name, value = header.split(':', 1)
                    headers[name.strip()] = value.strip()
            
            headers["User-Agent"] = UserAgent().random if args.random_agent else "git+Subprober/V1.XD"
            
            async with aiohttp.ClientSession(loop=loop) as session:
            
                async with session.request(args.method.upper(),url, headers=headers,ssl=False, proxy=args.proxy, timeout=timeout, allow_redirects=redirect, max_redirects=args.max_redirection) as response:
                    baseurl = url   
                    response_text = await response.content.read()
                    
                if args.cname:
                   cname = await __getcname__(url, "CNAME", args)
                   cname = cname if cname else ""
                   
                if args.ipaddress:
                    ip = await __getip__(url, "A", args)
                    ip = ip if ip else ""
                
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
                    
                    cnames = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{green}{cname}{reset}{bold}{white}]{reset} " if args.cname else ""
                    
                else:
                    
                    cnames = f"[{cname}]" if args.cname else ""
                    
                if not args.no_color:
                    
                    ips = f"{bold}{white}[{reset}{bold}{yellow}{ip}{bold}{white}]{reset}{reset} " if args.ipaddress else ""
                    
                else:
                    
                    ips = f"[{ip}]" if args.ipaddress else ""
                
                
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
                        
                status_code = status if args.status_code else ""
                
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
            
                        result = f"""{url} {gword}{status_code}{title}{server}{content}{word}{redirect}{cnames}{ips}"""
                    
                        print(f"{result}\n")
                
                        await save(result, args)
                        
                if args.exclude  and not args.match:
                    
            
                    if str(response.status) not in args.exclude:
            
                        result = f"""{url} {gword}{status_code}{title}{server}{content}{word}{redirect}{cnames}{ips}"""
                    
                        print(f"{result}\n")
                
                        await save(result, args)
                                    
                            
                if args.match and str(response.status) in args.match:
                
                        result = f"""{url} {gword}{status_code}{title}{server}{content}{word}{redirect}{cnames}{ips}"""
                        
                        print(f"{result}\n")
                        await save(result, args)
                        
                await asyncio.sleep(0.000001)
                if args.screenshot:
                    await screenshots(args, baseurl)
                                              
    except KeyboardInterrupt as e:
    
        print(f"[{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        SystemExit
    
    except aiohttp.ClientConnectorError as e:
        pass
        
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
        if args.secret_debug:
            print(f"Exception at request: {e}, {type(e)}")
    
    finally:
        bar()
        sem.release()
    
    
async def __initiate__(urls,args, sem, bar):
    
    try:        
        tasks = []
        customloops = uvloop.new_event_loop()
        asyncio.set_event_loop(loop=customloops)
        loops = asyncio.get_event_loop()
        
        for url in urls:
            await sem.acquire()
            task = asyncio.ensure_future(__probe__(url, args, sem, bar, loops))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
    except KeyboardInterrupt as e:
        SystemExit
    
    except asyncio.CancelledError as e:
        SystemExit
        
    except Exception as e:
        if args.secret_debug:
            print(f"Exception at initiate: {e}, {type(e)}")
            
        
        
    
async def __core__(args, url_list):
    
    try:            
                        
        url_lists = list(set(url_list))
        
        sem = asyncio.BoundedSemaphore(args.concurrency)
        
        customloops = uvloop.new_event_loop()
        asyncio.set_event_loop(loop=customloops)
        loops = asyncio.get_event_loop()
        
        with alive_bar(title=f"SubProber", total=len(url_lists), enrich_print=False) as bar:
                
                loops.run_until_complete(await __initiate__(url_lists, args, sem, bar))
                
    except KeyboardInterrupt as e:
        
        print(f"\n[{bold}{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        SystemExit
        
    except asyncio.CancelledError as e:  
        SystemExit
    except RuntimeError as e:
        SystemExit
    except Exception as e:
        if args.secret_debug:
            print(f"Exception At concurrents: {e}, {type(e)}")