#!/usr/bin/python3
import httpx 
import os  
from colorama import Fore,Back,Style
import argparse
import concurrent.futures 
import requests
from bs4 import BeautifulSoup
import time as t
import warnings
import random
import sys

red =  Fore.RED

green = Fore.GREEN

magenta = Fore.MAGENTA

cyan = Fore.CYAN

mixed = Fore.RED + Fore.BLUE

blue = Fore.BLUE

yellow = Fore.YELLOW

white = Fore.WHITE

reset = Style.RESET_ALL

bold = Style.BRIGHT

colors = [ green, cyan, blue]

random_color = random.choice(colors)


banner = ''' 

   _____       __                     __             
  / ___/__  __/ /_  _________  ____  / /_  ___  _____
  \__ \/ / / / __ \/ ___/ __ \/ __ \/ __ \/ _ \/ ___/
 ___/ / /_/ / /_/ / /  / /_/ / /_/ / /_/ /  __/ /    
/____/\__,_/_.___/_/  / .___/\____/_.___/\___/_/     
                     /_/                             
                
                
                            Author : D.Sanjai Kumar

                                                                         
                                                  '''
                                                  
                                                  
url_list = []

url_list = list(set(url_list))




parser = argparse.ArgumentParser(description=f"{bold}{white}A fast Probing tool for subdomains to get esssential Informations")

parser.add_argument("-f", "--filename", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}A filename that contains list of subdomains to probe and find status codes and other informations", type=str)

parser.add_argument("-u", "--url", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}A url to probe to find status codes and other informations", type=str )

parser.add_argument("-o", "--output", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Filename to write the output", type=str)

parser.add_argument("-c", "--concurrency", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Concurrency level for Multiple process", type=int, default=10)

parser.add_argument("-tl", "--title", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Get Title of subdomains", action="store_true")

parser.add_argument("-sv", "--server", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Get server of subdomains ", action="store_true")

parser.add_argument("-wc", "--word-count", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Get content length of subdomains", action="store_true")

parser.add_argument("-apt", "--application-type", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Get application type of subdomains", action="store_true")

parser.add_argument("-ex", "--exclude", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Exclude the particular response status code", type=str, nargs="*")

parser.add_argument("-mc", "--match", help=f"[{bold}{blue}INFO{reset}]:  {bold}{white}the particular response status code", type=str, nargs="*")

parser.add_argument("-suo", "--save-urls-only", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Save only urls for particular status codes instead of other informations", type=str, nargs="*") 

parser.add_argument("-s", "--silent", help=f"[{blue}INFO{reset}]: {bold}{white}Switching silent will not print Subprober banner and version", action="store_true")

parser.add_argument("-v", "--verbose", help=f"[{blue}INFO{reset}]: {bold}{white}Switching Verbose to console the results", action="store_true")

parser.add_argument("-cs", "--concise", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Switching Consice to console time out or request failured urls or subdomains", action="store_true")

parser.add_argument("-exs", "--excluded-save", help=f"[{blue}INFO{reset}]: {bold}{white}Switching Exluded save the excluded status codes results when --exclude switch is enabled", action="store_true")

parser.add_argument("-ums", "--unmatch-save", help=f"[{blue}INFO{reset}]: {bold}{white}Switching Unmatch save the Unmatched status codes results when --match switch is enabled", action="store_true")

parser.add_argument("-up", "--update", help=f"[{bold}{blue}INFO{reset}]: {bold}{white}Update the Subprober to latest version through pip{reset}", action="store_true")


args = parser.parse_args()


def get_version():
    
    version = "v1.0.2"
    
    url = f"https://api.github.com/repos/sanjai-AK47/Subprober/releases/latest"
    
    try:
        
        
        response = requests.get(url)
        
        if response.status_code == 200:
            
            data = response.json()
            
            latest = data.get('tag_name')
            
            if latest == version:
                
                message = "latest"
                
                print(f"[{blue}Version{reset}]: Subprober current version {version} ({green}{message}{reset})")
                
                t.sleep(1)
                
            else:
                
                message ="outdated"
                
                print(f"[{blue}Version{reset}]: Subprober current version {version} ({red}{message}{reset})")
                
                t.sleep(1)
                
        else:
            
            pass
        
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: Subprober says BYE!")
        
        exit()
        
                
    except Exception as e:
        
        pass
    
def Im_here():
    
    try:
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            
            futures = [executor.submit(send_request, url) for url in url_list]
            
        concurrent.futures.wait(futures)
        
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: Subprober says BYE!")
        
        exit()
        
    except Exception as e:
        
        pass
    
def Im_here_too():
    
    try:
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            
            futures = [executor.submit(match_me, url) for url in url_list]
            
        concurrent.futures.wait(futures)
        
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: Subprober says BYE!")
        
        exit()
        
    except Exception as e:
        
        pass
    
    
def match_me(url) :
    
    
    try:
        
        with httpx.Client(verify=False) as requests:
            
            
            
            response = requests.get(url)
            
        server1 =  response.headers.get("server")
        
        content_type = response.headers.get("Content-Type")
        
        if content_type:
            
            content_type = content_type.split(";")[0].strip()
            
            
        with warnings.catch_warnings():
                
                
                warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
            
                soup = BeautifulSoup(response.content, "html.parser")
    
                text = soup.get_text() 
    
    
        word_count = len(text.split())  
            
        title = soup.title.string
        
        server = server1 if args.server else ""
                
        content = content_type if args.application_type else ""
                
        word =  word_count if args.word_count else ""
        
        title = title if args.title else ""
        
        if str(response.status_code) in args.match:
            
            if response.status_code >1 and response.status_code <= 299   :
            
                result = f"{bold}{white}{url}[{bold}{green}{response.status_code}{reset}][{bold}{magenta}{server}{reset}][{bold}{yellow}{content}{reset}][{bold}{cyan}{title}{reset}][{cyan}{word}{reset}]"
                            
            if response.status_code >299 and response.status_code <= 399 :
            
                result = f"{bold}{white}{url}[{bold}{yellow}{response.status_code}{reset}][{bold}{magenta}{server}{reset}][{bold}{yellow}{content}{reset}][{bold}{cyan}{title}{reset}][{cyan}{word}{reset}]"
                
            if response.status_code > 399 and response.status_code <= 1000:
            
                result = f"{bold}{white}{url}[{bold}{red}{response.status_code}{reset}][{bold}{magenta}{server}{reset}][{bold}{yellow}{content}{reset}][{bold}{cyan}{title}{reset}][{cyan}{word}{reset}]" 
                        
            if args.verbose:
                
                print(result)
                
                if args.save_urls_only:
                    
                    if str(response.status_code) in args.save_urls_only:
                                
                                save_url_only(url)
                                
                elif not args.save_urls_only:
                                
                                save(result)
                
            if not args.verbose:
                
                if args.save_urls_only:
                    
                    if str(response.status_code) in args.save_urls_only:
                                
                                save_url_only(url)
                                
                elif not args.save_urls_only:
                                
                                save(result)
                
        if args.match and args.unmatch_save:
            
            if str(response.status_code) not in args.match:
                
                if str(response.status_code) in args.match:
            
                    if response.status_code >1 and response.status_code <= 299   :
            
                     result = f"{bold}{white}{url}[{bold}{green}{response.status_code}{reset}][{bold}{magenta}{server}{reset}][{bold}{yellow}{content}{reset}][{bold}{cyan}{title}{reset}][{cyan}{word}{reset}]"
                            
                if response.status_code >299 and response.status_code <= 399 :
            
                    result = f"{bold}{white}{url}[{bold}{yellow}{response.status_code}{reset}][{bold}{magenta}{server}{reset}][{bold}{yellow}{content}{reset}][{bold}{cyan}{title}{reset}][{cyan}{word}{reset}]"
                
                if response.status_code > 399 and response.status_code <= 1000:
            
                    result = f"{bold}{white}{url}[{bold}{red}{response.status_code}{reset}][{bold}{magenta}{server}{reset}][{bold}{yellow}{content}{reset}][{bold}{cyan}{title}{reset}][{cyan}{word}{reset}]" 
                    
                    
                if args.save_urls_only:
                    
                    if str(response.status_code) in args.save_urls_only:
                                
                                save_url_only(url)
                                
                elif not args.save_urls_only:
                                
                                save(result)
                        
                    
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: Subprober says BYE!")
        
        exit()
        
    except httpx.TimeoutException as e:
        
        if args.concise:
            
            print(f"[{bold}{red}TIME-OUT{reset}]: {bold}{white}{url}{reset}")
            
        else:
            
            pass 
        
    except Exception as e:
        
        pass 
        
        
    

    
def send_request(url):
    
    try:
        
        with httpx.Client(verify=False) as requests:
            
            
            
            response = requests.get(url)
            
        server1 =  response.headers.get("server")
        
        content_type = response.headers.get("Content-Type")
        
        if content_type:
            
            content_type = content_type.split(";")[0].strip()
            
            
        with warnings.catch_warnings():
                
                
                warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
            
                soup = BeautifulSoup(response.content, "html.parser")
    
                text = soup.get_text() 
    
    
        word_count = len(text.split())  
            
        title = soup.title.string
        
        server = server1 if args.server else ""
                
        content = content_type if args.application_type else ""
                
        word =  word_count if args.word_count else ""
        
        title = title if args.title else ""
                
                     
        
        
        if response.status_code >1 and response.status_code <= 299   :
            
            result = f"{bold}{white}{url}[{bold}{green}{response.status_code}{reset}][{bold}{magenta}{server}{reset}][{bold}{yellow}{content}{reset}][{bold}{cyan}{title}{reset}][{bold}{cyan}{word}{reset}]"

            if args.verbose:
                    
                
                if args.exclude:
                    
                    if str(response.status_code) in args.exclude:
                        
                        if args.excluded_save:
                            
                            if args.save_urls_only:
                                
                                if str(response.status_code) in args.save_urls_only:
                                
                                    save_url_only(url)
                                
                            elif not args.save_urls_only:
                                
                                save(result)
                            
                        else:
                            
                            pass
                        
                if not args.exclude:
                        
                        print(result)
                
                        if args.save_urls_only:
                            
                            if str(response.status_code) in args.save_urls_only:
                                
                                    save_url_only(url)
                                
                        elif not args.save_urls_only:
                                
                                save(result)
                
            if not args.verbose:
                
                if args.exclude:
                    
                    if str(response.status_code) in args.exclude:
                        
                        if args.excluded_save:
                            
                            if args.save_urls_only:
                                
                                if str(response.status_code) in args.save_urls_only:
                                
                                    save_url_only(url)
                                
                            elif not args.save_urls_only:
                                
                                save(result)
                            
                        else:
                            
                            pass
                
                if not args.exclude:
                    
                    if args.save_urls_only:
                        
                        if str(response.status_code) in args.save_urls_only:
                                
                                save_url_only(url)
                                
                    elif not args.save_urls_only:
                                
                                save(result)
                
        if response.status_code >299 and response.status_code <= 399 :
            
            result = f"{bold}{white}{url}[{bold}{yellow}{response.status_code}{reset}][{bold}{magenta}{server}{reset}][{bold}{yellow}{content}{reset}][{bold}{cyan}{title}{reset}][{bold}{cyan}{word}{reset}]"
        
            if args.verbose:
                    
                
                if args.exclude:
                    
                    if str(response.status_code) in args.exclude:
                        
                        if args.excluded_save:
                            
                            if args.save_urls_only:
                                
                                if str(response.status_code) in args.save_urls_only:
                                
                                    save_url_only(url)
                                
                            elif not args.save_urls_only:
                                
                                save(result)
                            
                        else:
                            
                            pass
                        
                if not args.exclude:
                        
                        print(result)
                
                        if args.save_urls_only:
                            
                            if str(response.status_code) in args.save_urls_only:
                                
                                save_url_only(url)
                                
                        elif not args.save_urls_only:
                                
                                save(result)
                
            if not args.verbose:
                
                if args.exclude:
                    
                    if str(response.status_code) in args.exclude:
                        
                        if args.excluded_save:
                            
                            if args.save_urls_only:
                                
                                if str(response.status_code) in args.save_urls_only:
                                
                                    save_url_only(url)
                                
                            elif not args.save_urls_only:
                                
                                save(result)
                            
                        else:
                            
                            pass
                
                if not args.exclude:
                    
                    if args.save_urls_only:
                        
                        if str(response.status_code) in args.save_urls_only:
                                
                                save_url_only(url)
                                
                    elif not args.save_urls_only:
                                
                                save(result)
                
        if response.status_code > 399 and response.status_code <= 1000:
            
            result = f"{bold}{white}{url}[{bold}{red}{response.status_code}{reset}][{bold}{magenta}{server}{reset}][{bold}{yellow}{content}{reset}][{bold}{cyan}{title}{reset}][{bold}{cyan}{word}{reset}]"
        
            if args.verbose:
                    
                
                if args.exclude:
                    
                    if str(response.status_code) in args.exclude:
                        
                        if args.excluded_save:
                            
                            if args.save_urls_only:
                                
                                if str(response.status_code) in args.save_urls_only:
                                
                                    save_url_only(url)
                                
                            elif not args.save_urls_only:
                                
                                save(result)
                            
                        else:
                            
                            pass
                        
                if not args.exclude:
                        
                        print(result)
                
                        if args.save_urls_only:
                            
                            if str(response.status_code) in args.save_urls_only:
                                
                                save_url_only(url)
                                
                        elif not args.save_urls_only:
                                
                                save(result)
                
            if not args.verbose:
                
                if args.exclude:
                    
                    if str(response.status_code) in args.exclude:
                        
                        if args.excluded_save:
                            
                            if args.save_urls_only:
                                
                                if str(response.status_code) in args.save_urls_only:
                                
                                    save_url_only(url)
                                
                            elif not args.save_urls_only:
                                
                                save(result)
                            
                        else:
                            
                            pass
                        if args.excluded_save:
                            
                            if args.save_urls_only:
                                
                                if str(response.status_code) in args.save_urls_only:
                                
                                    save_url_only(url)
                                
                            elif not args.save_urls_only:
                                
                                save(result)
                            
                        else:
                            
                            pass
                
                if not args.exclude:
                    
                    if args.save_urls_only:
                        
                        if str(response.status_code) in args.save_urls_only:
                                
                                save_url_only(url)
                                
                    elif not args.save_urls_only:
                                
                                save(result)
            
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: Subprober says BYE!")
        
        exit()
      
    except httpx.TimeoutException as e:
        
        if args.concise:
            
            print(f"[{bold}{red}TIME-OUT{reset}]: {bold}{white}{url}{reset}")
            
        else:
            
            pass     
        
    except Exception as e:
        
        pass 
            

def save(url):
    
    try:
    
        if args.output:
            
            if os.path.isfile(args.output):
                
                filename = args.output
                
            elif os.path.isdir(args.output):
                
                filename = os.path.join(args.output, f"subprober_results.txt")
                
            else:
                
                filename = args.output
                
        if not args.output:
            
            filename = f"subprober_results.txt"
            
        
        with open(filename, "a") as w:
            
            w.write(url + '\n')
            
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: Subprober says BYE!")
        
        exit()
        
    except Exception as e:
        
        pass
    
def save_url_only(url):
    
    try:
    
        if args.output:
            
            if os.path.isfile(args.output):
                
                filename = args.output
                
            elif os.path.isdir(args.output):
                
                filename = os.path.join(args.output, f"subprober_results.txt")
                
            else:
                
                filename = args.output
                
        if not args.output:
            
            filename = f"subprober_results.txt"
            
        
        with open(filename, "a") as w:
            
            w.write(url + '\n')
            
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: Subprober says BYE!")
        
        exit()
        
    except Exception as e:
        
        pass

def main():
    
    try:
        
        if args.url and not args.filename :
            
            if not args.silent:
            
                print(f"{bold}{random_color}{banner}{reset}")
            
                get_version()
            
            if args.url and args.verbose:
            
                print(f"[{blue}INFO{reset}]: Verbose mode Enabled. Now Subprober console the output to you! ")
                
            if args.url and not args.verbose:
                
                print(f"[{red}INFO{reset}]: Verbose mode not Enabled. Now Subprober not console the output to you! ")
                
        if  args.url and args.output:

            print(f"[{green}INFO{reset}]: Output will be saved in {args.output}")
            
        elif  args.url and not args.output:
        
        
            print(f"[{green}INFO{reset}]: Output will be saved in subprober_results.txt")


        if args.url and args.concurrency:
            

            print(f"[{green}INFO{reset}]: Concurrency Enabled by user")
            

        if args.url and args.concurrency > 50:
            

            print(f"[{red}INFO{reset}]: Your Concurrency level {args.concurrency} is greater than 50 ")

            t.sleep(1)

            print(f"[{red}CAUTION{reset}]: High Concurrency level may cause race condition and inacurrate results ")

        else:

            pass
        
        if args.url and not args.concurrency:
        

            print(f"[{red}INFO{reset}]: User Not defined concurrency level and Continuing with default level {args.concurrency}")
            
        if args.url  and not args.filename:
            
            
            url = args.url

            if url.startswith("https://") or url.startswith("http://"):
           
                 url_list.append(url)
             
            elif not  url.startswith("https://") or url.startswith("http://"):
                
               new_url = f"https://{url}"
               
               new_http = f"http://{url}"
               
               url_list.append(new_url)
               
               url_list.append(new_http)
            
        if args.url and args.match:
                
                Im_here_too()
                
        elif args.url and not args.match:
                
                Im_here()
                
        elif args.exclude and args.match:
                
                print(f"[{bold}{red}FLAG-ERROR{reset}]: Please provide either --exclude or --match")
                
                exit()
        
        
        
        if args.filename and not args.url:
            
                if not args.silent:
                
                    print(f"{bold}{random_color}{banner}{reset}")
            
                    get_version()
            
                if args.filename and args.verbose:
            
                    print(f"[{blue}INFO{reset}]: Verbose mode Enabled. Now Subprober console the output to you! ")
                
                if args.filename and not args.verbose:
                
                    print(f"[{red}INFO{reset}]: Verbose mode not Enabled. Now Subprober not console the output to you! ")
                
                if  args.filename and args.output:

                    print(f"[{green}INFO{reset}]: Output will be saved in {args.output}")
            
                elif args.filename and not args.output:
        
        
                    print(f"[{green}INFO{reset}]: Output will be saved in subprober_results.txt")
        
                if args.filename and args.concurrency:
            

                    print(f"[{green}INFO{reset}]: Concurrency Enabled by user")
            

                    if args.filename and args.concurrency > 50:
            

                        print(f"[{red}INFO{reset}]: Your Concurrency level {args.concurrency} is greater than 50 ")

                        t.sleep(1)

                        print(f"[{red}CAUTION{reset}]: High Concurrency level may cause race condition and inacurrate results ")

                    else:

                        pass
        
                if args.filename and not args.concurrency:
        

                    print(f"[{red}INFO{reset}]: User Not defined concurrency level and Continuing with default level {args.concurrency}")
                    
                if args.filename and not args.url:
                    
                    
                    try:
                    
                        filename = args.filename
                    
                        with open(filename, "r") as urls:
                        
                            lists = urls.read().splitlines()
                        
                        for url in lists:
                        
                            if url.startswith("https://") or url.startswith("http://") :
                        
                                url_list.append(url)
                            
                            elif not  url.startswith("https://") or url.startswith("http://") :
                            
                                new_url = f"https://{url}"
                                
                                new_http = f"http://{url}"
                            
                                url_list.append(new_url)
                                
                                url_list.append(new_http)
                                
                        if args.url and args.match:
                
                            Im_here_too()
                
                        elif args.url and not args.match:
                
                            Im_here()
                
                        elif args.exclude and args.match:
                
                            print(f"[{bold}{red}FLAG-ERROR{reset}]: Please provide either --exclude or --match")
                
                            exit()
                        
                        
                        
                    except FileNotFoundError as e:
                    
                        print(f"[{red}INFO{reset}]: {args.filename} not found. please check the file or file path exist or not!")
                        
        
        if args.update:
            
            version = "v1.0.2"
    
            url = f"https://api.github.com/repos/sanjai-AK47/Subprober/releases/latest"
    
            try:
        
        
                response = requests.get(url)
        
                if response.status_code == 200:
            
                    data = response.json()
            
                    latest = data.get('tag_name')
            
                    if latest == version:
                
                
                        print(f"[{bold}{blue}Version{reset}]: {bold}{white}Subprober already in latest version dont worry :){reset}")
                
                        t.sleep(1)
                        
                        exit()
                
                    else:
                        
                        try:
                            
                            print(f"[{bold}{blue}UPDATE{reset}]: {bold}{white}Updating the Subprober{reset}")
                
                            os.system("pip install --upgrade subprober")
                            
                            print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Please check whether Subprober updated to latest version or update it through manually{reset}")
                            
                            exit()
                            
                            
                        except Exception as e:
                            
                            print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober update failed due to some error{reset}")
                            
                            exit()
                
                else:
            
                    print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober update failed due to some error{reset}")
                    
                    exit()
                    
            except KeyboardInterrupt as e:
        
                print(f"[{blue}INFO{reset}]: Subprober says BYE!")
        
                exit()
        
            except httpx.TimeoutException as e:
        
                print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober update failed due to failed to reach Subprober Repository please report this issue{reset}")
        
                exit()
                
            except Exception as e:
                
                print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober update failed due to failed to reach Subprober Repository please report this issue{reset}")
       
                exit()
          
                    
        if not args.filename and not args.url:
            
            try:
                
                if not args.silent:
                    
                    print(f"{bold}{random_color}{banner}{reset}")
            
                    get_version()
                
                for line in sys.stdin:
                      
                      url = line.strip()
                      
                      if url.startswith("https://") or url.startswith("http://"):
                          
                             url_list.append(url)
                      else:
                         
                          new_url = f"https://{url}"
                          
                          new_http = f"http://{url}"
                          
                          url_list.append(new_url)
                          
                          url_list.append(new_http)
                          
                if not args.url and not args.filename and args.match:
                
                    Im_here_too()
                
                elif not args.url and not args.filename and not args.match:
                
                    Im_here()
                
                elif not args.url and not args.filename and args.exclude and args.match:
                
                    print(f"[{bold}{red}FLAG-ERROR{reset}]: Please provide either --exclude or --match")
                
                    exit()
                          
            except KeyboardInterrupt as e:
                
                   print(f"[{blue}INFO{reset}]: Subprober says BYE!")
                   
                   exit()
                   
            except Exception as e:
                
                   print(f"[{blue}INFO{reset}]: Stdin Error occured for Subprober")
                   
                   exit()
            
    except KeyboardInterrupt as e:
        
        print(f"[{blue}INFO{reset}]: Subprober says BYE!")
        
    except Exception as e:
        
        print(f"[{blue}INFO{reset}]:Unknow error occured due to : {e}, please report this issue in Subprober github page")

if __name__ == "__main__" :
    
    main() 
    