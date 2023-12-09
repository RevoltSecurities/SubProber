#!/usr/bin/env python3
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
from alive_progress import alive_bar
import sys

requests.packages.urllib3.disable_warnings()

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

def help_me():
    
    print(f"""
          
{bold}{white}Subprober - A Fast Probing Tool for Penetration testing

{bold}[{bold}{blue}Description{reset}] :

    {bold}{white}Subprober is a high-performance tool designed for probing and  extract vital information efficiently.{reset}

{bold}[{bold}{blue}Flags{reset}]:{reset}{bold}{white}

    -f, --filename            Specify the filename containing a list of subdomains for targeted probing. 
                              This flag is used to find and analyze status codes and other pertinent details.
                      
    -h, --help                Show this help message for you and exit!
    
    -u, --url                 Specify a target URL for direct probing. This flag allows for the extraction of 
                              status codes and other valuable information.
                      
    -sp. --show-progress      Enable show prgress mode which will show the progress of the Subprober with progress bar like this ( example: |████████████████████████████████████████| 4000/4000 [100%] in 12.4s (3.23/s) ).


    -o, --output              Define the output filename to store the results of the probing operation.

    -c, --concurrency         Set the concurrency level for multiple processes. Default is 10.

    -tl, --title              Retrieve and display the title of subdomains.

    -to, --timeout            Set a custom timeout value for sending requests.

    -sv, --server             Identify and display the server information associated with subdomains.

    -wc, --word-count         Retrieve and display the content length of subdomains.

    -apt, --application-type  Determine and display the application type of subdomains.

    -ex, --exclude            Exclude specific response status code(s) from the analysis.

    -mc, --match              Specify specific response status code(s) to include in the analysis.

    -suo, --save-urls-only    Save only URLs for particular status codes, excluding other information.

    -s, --silent              Enable silent mode to suppress the display of Subprober banner and version information.

    -v, --verbose             Enable verbose mode to display detailed results on the console.

    -cs, --concise            Enable concise mode to display only timeout or request failure URLs or subdomains.

    -exs, --excluded-save     Save the results of excluded status codes when the --exclude switch is enabled.

    -ums, --unmatch-save      Save the results of unmatched status codes when the --match switch is enabled.

    -up, --update             Update Subprober to the latest version through pip.{reset}

{bold}{white}[{bold}{blue}INFO{reset}]:{bold}{white}

    subprober -f subdomains.txt -o output.txt -tl -wc -sv -v -apt -wc -ex 404 500 -suo 200 -v -o output.txt -c 
    
    subprober -u https://example.com -c 20 -to 8  -tl -sv  -wc -apt -ex 404 500 -suo 200 -v -o output.txt
    
    cat subdomains.txt | subprober -c 20 -to 8 -tl -sv -wc -apt -ex 404 500 -suo 200 -v -o output.txt
    {reset}""")
    
    exit()




banner = f''' 

   _____       __    ____             __             
  / ___/__  __/ /_  / __ \_________  / /_  ___  _____
  \__ \/ / / / __ \/ /_/ / ___/ __ \/ __ \/ _ \/ ___/
 ___/ / /_/ / /_/ / ____/ /  / /_/ / /_/ /  __/ /    
/____/\__,_/_.___/_/   /_/   \____/_.___/\___/_/     
                                                         
                
                
                    {bold}{white}Author : D.Sanjai Kumar @CyberRevoltSecurities{reset}

                                                                         
                                                  '''
                                                  
                                                  
url_list = []

url_list = list(set(url_list))




parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("-f", "--filename",  type=str)

parser.add_argument("-h", "--help", action="store_true")

parser.add_argument("-sp", "--show-progress", action="store_true")

parser.add_argument("-u", "--url",  type=str )

parser.add_argument("-o", "--output", type=str)

parser.add_argument("-c", "--concurrency", type=int, default=10)

parser.add_argument("-tl", "--title", action="store_true")

parser.add_argument("-to", "--timeout", type=int)

parser.add_argument("-sv", "--server", action="store_true")

parser.add_argument("-wc", "--word-count",  action="store_true")

parser.add_argument("-apt", "--application-type",  action="store_true")

parser.add_argument("-ex", "--exclude",  type=str, nargs="*")

parser.add_argument("-mc", "--match",  type=str, nargs="*")

parser.add_argument("-suo", "--save-urls-only", type=str, nargs="*") 

parser.add_argument("-s", "--silent", action="store_true")

parser.add_argument("-v", "--verbose", action="store_true")

parser.add_argument("-cs", "--concise",  action="store_true")

parser.add_argument("-exs", "--excluded-save",  action="store_true")

parser.add_argument("-ums", "--unmatch-save", action="store_true")

parser.add_argument("-up", "--update", action="store_true")


args = parser.parse_args()


def get_version():
    
    version = "v1.0.3"
    
    url = f"https://api.github.com/repos/sanjai-AK47/Subprober/releases/latest"
    
    try:
        
        
        
        response = requests.get(url, verify=False, timeout=10)
        
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
        
        if args.show_progress:
        
            with alive_bar(len(url_list), enrich_print=False) as bar:
        
                with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            
                    futures = [executor.submit(send_request, url) for url in url_list]
            
                    for futures in concurrent.futures.as_completed(futures):
            
                        bar()
        else:
            
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
        
        if args.show_progress:
        
            with alive_bar(len(url_list), enrich_print=False) as bar:
        
                with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            
                    futures = [executor.submit(match_me, url) for url in url_list]
                
                    for futures in concurrent.futures.as_completed(futures):
                        
                        bar()
                        
                        
        else:
                
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
        
        timeout= args.timeout if args.timeout else 10
   
        response = requests.get(url, verify=False, timeout=timeout)
            
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
        
    except requests.RequestException as e:
        
        if args.concise:
            
            print(f"[{bold}{red}TIME-OUT{reset}]: {bold}{white}{url}{reset}")
            
        else:
            
            pass 
        
    except Exception as e:
        
        pass 
        
        
    

    
def send_request(url):
    
    try:
        
        
            
        timeout= args.timeout if args.timeout else 10
            
        response = requests.get(url, verify=False, timeout=timeout)
            
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
      
    except requests.RequestException as e:
        
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
        
        if args.url and not args.filename:
            
            if not args.silent:
            
                print(f"{bold}{random_color}{banner}{reset}", file=sys.stderr)
            
                get_version()
                
            if  args.exclude and args.match:
                
                    print(f"[{bold}{red}FLAG-ERROR{reset}]: Please provide either --exclude or --match")
                
                    exit()
            
            if args.url and args.verbose:
            
                print(f"[{blue}INFO{reset}]: Verbose mode Enabled. Now Subprober console the output to you! ")
                
            if args.url and not args.verbose:
                
                print(f"[{red}INFO{reset}]: Verbose mode not Enabled. Now Subprober not console the output to you! ")
                
            if  args.url and args.output:

                print(f"[{green}INFO{reset}]: Output will be saved in {args.output}")
            
            elif  args.url and not args.output:
        
        
                print(f"[{green}INFO{reset}]: Output will be saved in subprober_results.txt")


            if  args.concurrency:
            

                print(f"[{green}INFO{reset}]: Concurrency Enabled by user")
            

        
            if  not args.concurrency:
        

                print(f"[{red}INFO{reset}]: User Not defined concurrency level and Continuing with default level {args.concurrency}")
                
            
            
            if args.url and not args.filename:
            
            
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
        
        
        
        if args.filename and not args.url:
            
                if not args.silent:
                
                    print(f"{bold}{random_color}{banner}{reset}")
            
                    get_version()
                    
                if args.exclude and args.match:
                
                            print(f"[{bold}{red}FLAG-ERROR{reset}]: Please provide either --exclude or --match")
                
                            exit()
            
                if  args.verbose:
            
                    print(f"[{blue}INFO{reset}]: Verbose mode Enabled. Now Subprober console the output to you! ")
                
                if  not args.verbose:
                
                    print(f"[{red}INFO{reset}]: Verbose mode not Enabled. Now Subprober not console the output to you! ")
                
                if   args.output:

                    print(f"[{green}INFO{reset}]: Output will be saved in {args.output}")
            
                elif  not args.output:
        
        
                    print(f"[{green}INFO{reset}]: Output will be saved in subprober_results.txt")
        
                if  args.concurrency:
            

                    print(f"[{green}INFO{reset}]: Concurrency Enabled by user")
            

        
                if  not args.concurrency:
        

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
                                
                        if args.match:
                
                            Im_here_too()
                
                        elif not args.match:
                
                            Im_here()
                
                        
                        
                        
                        
                    except FileNotFoundError as e:
                    
                        print(f"[{red}INFO{reset}]: {args.filename} not found. please check the file or file path exist or not!")
                        
                    except Exception as e:
                        
                        pass
                        
        
        if args.update:
            
            version = "v1.0.3"
    
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
                
        if args.help:
            
            print(f"{bold}{random_color}{banner}{reset}", file=sys.stderr)
            
            help_me()
          
                    
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
                          
                if args.match:
                
                    Im_here_too()
                
                elif  not args.match:
                
                    Im_here()
                
                elif  args.exclude and args.match:
                
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
    