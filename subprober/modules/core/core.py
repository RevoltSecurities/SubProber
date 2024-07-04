#!/usr/bin/python3
import asyncio
import httpx
from aiohttp.client_exceptions import ClientResponseError, ClientPayloadError, InvalidURL
import aiofiles
import os  
from colorama import Fore,Style
import jarm.scanner
import jarm.scanner.scanner
import requests
from bs4 import BeautifulSoup
import time as t
import warnings
import random
from alive_progress import alive_bar
import urllib3
from aiohttp import client_exceptions
requests.packages.urllib3.disable_warnings()
from bs4 import  XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
import uvloop
from .screenshot.screenshot import *
from .probes.probes import __getcname__, __getip__
from fake_useragent import UserAgent
import re
import jarm
warnings.simplefilter('ignore', RuntimeWarning)



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
    
    
async def jarmhashes(url):
    try:
        pattern = r'^(?:https?://)?((?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*)'
        extracted = re.match(pattern, url)
        domain = extracted.group(1)
        hasher = jarm.scanner.scanner.Scanner
        jarms = await hasher.scan_async(domain, 443)
        hash = jarms[0]
        return hash
    except Exception as e:
        pass


async def __probe__(url, args, sem, bar, session):
    
    try:
            
        warnings.filterwarnings("ignore", category=ResourceWarning)
            
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                        
        headers={}
            
        timeout = args.timeout
            
        redirect = True if args.allow_redirect else False
            
        if args.header:
            for header in args.header:
                name, value = header.split(':', 1)
                headers[name.strip()] = value.strip()
            
        headers["User-Agent"] = UserAgent().random if args.random_agent else "git+Subprober/V2.XD"
            
        response = await  session.request(args.method.upper(),url, headers=headers, timeout=timeout, follow_redirects=redirect)
        await asyncio.sleep(0.000001)
        baseurl = url   
        response_text = await response.aread()
        jarms_hash = await jarmhashes(baseurl) if args.jarm_fingerprint else ""
        
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
                
        httpv = response.http_version if response.http_version else ""
                
        reason = response.reason_phrase if response.reason_phrase else ""
        
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
            jarms = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{magenta}{jarms_hash}{reset}{bold}{white}]{reset}" if args.jarm_fingerprint else ""
        else :
            jarms = f"[{jarms_hash}]" if args.jarm_fingerprint else ""
                
        if not args.no_color:
            http_reason = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{yellow}{reason}{reset}{bold}{white}]{reset}" if args.http_reason else ""
        else:
            http_reason = f"[{reason}]" if args.http_reason else ""
                
                
        if not args.no_color:
            redirect = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{magenta}{rd}{reset}{bold}{white}]{reset}" if args.location else ""
        else:
            redirect = f"[{rd}]" if args.location else ""
                    
                    
        if not args.no_color:
            version = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{blue}{httpv}{reset}{bold}{white}]{reset} " if args.http_version else ""
        else:
            version = f"[{httpv}]" if args.http_version else ""


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
                       
                
        if response.status_code >=200 and response.status_code <=299:
                    
            if not args.no_color:
                status =f"{bold}{white}[{reset}{bold}{bold}{green}{response.status_code}{reset}{bold}{white}]{reset}"
            else:
                status =f"[{response.status_code}]"
                        
                    
        elif response.status_code >= 300 and response.status_code <=399:
                    
            if not args.no_color:
                status =f"{bold}{white}[{reset}{bold}{bold}{yellow}{response.status_code}{reset}{bold}{white}]{reset}"
            else:
                status =f"[{response.status_code}]"
                    
        else:
                    
            if not args.no_color:
                status =f"{bold}{white}[{reset}{bold}{red}{response.status_code}{reset}{bold}{white}]{reset}"
            else:
                status =f"[{response.status_code}]"
                        
                        
        status_code = status if args.status_code else ""
                
        if response.status_code >=200 and response.status_code <=299:
            if args.grep_word:
                if not args.no_color:
                    grep =f"{bold}{white}[{reset}{bold}{green}SUCCESS{reset}{bold}{white}]{reset}"
                else:
                    grep =f"[SUCCESS]"
                    
        elif response.status_code >= 300 and response.status_code <=399:
            if args.grep_word:
                if not args.no_color:
                    grep =f"{bold}{white}[{reset}{bold}{cyan}REDIRECTED{reset}{bold}{white}]{reset}"
                else:
                    grep =f"[RIDRECTED]"
                    
        else:
                    
            if args.grep_word:
                if not args.no_color:
                    grep =f"{bold}{white}[{reset}{bold}{red}ERROR{reset}{bold}{white}]{reset}"
                else:
                    grep =f"[ERROR]" 
                            
                            
        gword = grep if args.grep_word else ""
                        
        if not args.no_color:
            url = f"{bold}{white}{url}{reset}"
        else:
            url = f"{url}"
                    
                
        if args.exclude and str(response.status_code) in args.exclude:
            pass
                
                
        if not args.exclude  and not args.match:
            result = f"""{url} {gword}{http_reason}{status_code}{version}{title}{server}{content}{word}{redirect}{cnames}{ips}{jarms}"""
            print(f"{result}\n")
            await save(result, args)
                        
        if args.exclude  and not args.match:
            
            if str(response.status_code) not in args.exclude:
                result = f"""{url} {gword}{http_reason}{status_code}{version}{title}{server}{content}{word}{redirect}{cnames}{ips}{jarms}"""
                print(f"{result}\n")
                await save(result, args)
                                    
                            
        if args.match and str(response.status_code) in args.match:
                
            result = f"""{url} {gword}{http_reason}{status_code}{version}{title}{server}{content}{word}{redirect}{cnames}{ips}{jarms}"""
            print(f"{result}\n")
            await save(result, args)
                        
        if args.screenshot:
            await screenshots(args, baseurl)
                                              
    except KeyboardInterrupt as e:
    
        print(f"[{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        SystemExit
        
    except httpx.ConnectError as e:
        pass
    
   
    except httpx.Timeout as e:
        if args.verbose:
            print(f"[{bold}{red}INFO{reset}]: {bold}{white}Client Timeout Exceeds for: {url}{reset}")
            
    except httpx.RequestError as e:
        if args.verbose:
            print(f"[{bold}{red}INFO{reset}]: {bold}{white}Client Timeout Exceeds for: {url}{reset}")
    
    
    except asyncio.TimeoutError as e:
        if args.verbose:
            print(f"[{bold}{red}INFO{reset}]: {bold}{white}Client Timeout Exceeds for: {url}{reset}")
            
    except asyncio.CancelledError as e:
        SystemExit
        
    except UnicodeError as e:
        pass
    except httpx.InvalidURL as e:
        pass
    
    
    except Exception as e:
        if args.secret_debug:
            print(f"Exception at request: {e}, {type(e)}, {url}")

    finally:
        bar()
        sem.release()
    
    
async def __initiate__(urls,args, sem, bar, session):
    
    try:        
        tasks = []
        for url in urls:
            await sem.acquire()
            task = asyncio.ensure_future(__probe__(url, args, sem, bar, session))
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
        proxy = args.proxy if args.proxy else None
        http2 = True if args.http2 else False
        async with httpx.AsyncClient(verify=False, max_redirects=args.max_redirection, http2=http2) as session:
            with alive_bar(title="SubProber", total=len(url_lists), enrich_print=False) as bar:
                await __initiate__(url_lists, args, sem, bar, session)
                
    except KeyboardInterrupt:
        raise SystemExit
    except Exception as e:
        if args.secret_debug:
            print(f"Exception at concurrents: {e}, {type(e)}")