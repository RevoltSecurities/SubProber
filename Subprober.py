import httpx 
import os  
from colorama import Fore,Back,Style
import argparse
from concurrent.futures import ThreadPoolExecutor
import requests

import time as t

red =  Fore.RED

green = Fore.GREEN

magenta = Fore.MAGENTA

cyan = Fore.CYAN

mixed = Fore.RED + Fore.BLUE

blue = Fore.BLUE

yellow = Fore.YELLOW

white = Fore.WHITE

reset = Style.RESET_ALL


banner = ''' 

                 _____       _    ______          _               
                /  ___|     | |   | ___ \        | |              
                \ `--. _   _| |__ | |_/ / __ ___ | |__   ___ _ __ 
                 `--. \ | | | '_ \|  __/ '__/ _ \| '_ \ / _ \ '__|
                /\__/ / |_| | |_) | |  | | | (_) | |_) |  __/ |   
                \____/ \__,_|_.__/\_|  |_|  \___/|_.__/ \___|_|   
                                                  
                
                                            Author : D.Sanjai Kumar

                                                                         
                                                  '''

urls_list = []


parser = argparse.ArgumentParser(description="A fast tool to find http status code for Subdomains")

parser.add_argument("-f", "--filename", help=f"[{blue}INFO{reset}]: A filename that contains list of subdomains", type=str, required=True)

parser.add_argument("-o", "--output", help=f"[{blue}INFO{reset}]: Filename to write the output")

parser.add_argument("-c", "--concurrency", help=f"[{blue}INFO{reset}]: Concurrency level for Multiple process", type=int)

parser.add_argument("-v", "--verbose", help=f"[{blue}INFO{reset}]: Enabling Verbose to print the output to User", action="store_true")

args = parser.parse_args()


concurrency = args.concurrency

verbose = args.verbose

filename = args.filename

output_file = args.output


def get_version():
    
    version = "v1.0.0"
    
    url = f"https://api.github.com/repos/sanjai-AK47/Subdominator/releases/latest"
    
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
                
    except Exception as e:
        
        pass

def check_essentials():
    
    print(f"{green}{banner}{reset}")
    t.sleep(2)
    get_version()
    
    
    if filename:
        
        

        try:

        
            with open(filename,"r") as file:

                pass
            
            

            print(f"[{green}INFO{reset}]: Loading the given input from {filename} ")
            


        except Exception as e:

            print(f"{red}[!]Can't  read the {filename} check the file path or file exist{reset}")
            exit()

    if verbose:

        print(f"[{green}INFO{reset}]: Versbose Enabled by user")
    
    elif not verbose:

        print(f"[{red}INFO{reset}]: Verbose Not Enabled by user")

    else:

        print(f"[{red}INFO{reset}]: Verbose Not Enabled by user")

    
    if output_file is not None:

        print(f"[{green}INFO{reset}]: Output will be saved in {output_file}")
    else:
        
        output = "Subprober_results.txt"
        
        print(f"[{green}INFO{reset}]: Output will be saved in {output}")
        

    if concurrency:

        print(f"[{green}INFO{reset}]: Concurrency Enabled by user")

        if concurrency > 50:

            print(f"[{red}INFO{reset}]: Your Concurrency level {concurrency} is greater than 50 ")

            t.sleep(2)

            print(f"[{red}CAUTION{reset}]: High Concurrency level may cause race condition and inacurrate results ")

        else:

            pass
        
    else:
        
        default = 10

        print(f"[{red}INFO{reset}]: User Not defined concurrency level and Continuing with default level {default}")

            
            
def load_urls():
    
    try:
        filename = args.filename
        with open(filename, "r") as r:
            
            urls = r.read().splitlines()
            
            for url in urls:
                
                if url.startswith("*"):
                    
                    continue
            
                urls_list.append(f"https://{url}")
                
            with ThreadPoolExecutor(max_workers=concurrency) as executor:
        
                futures = [executor.submit(get_status_code,url)for url in urls_list]
        
                    
                
    except Exception as e:
        
        print(f"[{red}INFO{reset}]Can't  read the {filename} check the file path or file exist")
        
        exit()
        
def get_status_code(url):
    
    try:
        
        with httpx.Client() as client:
            
            response = client.get(url)
            
            status_code = response.status_code if response.status_code is not None else None

            if status_code is not None:
                
                if verbose:
                    
                    print(f"[{green}FOUND{reset}]: {url} - status code {status_code}")
                    
                else:
                    
                    pass

                if not output_file:
                    
                    with open("Subprober_results.txt", "a") as w:
                        
                        w.write(f"{url} - {status_code}\n")
                        
                elif output_file:
                    
                    with open(output_file, "a") as w:
                        
                        w.write(f"{url} - {status_code}\n")
                        
                else:
                    
                    print(f"[{red}INFO{reset}]: Something went wrong saving output")
                    
                    t.sleep(3)
                    
            else:
                
                if args.verbose:
                    
                    print(f"[{red}INFO{reset}]: {url} - Can't retrieve status code for this URL")
                    
                else: 
                    
                    pass

    except Exception as e:
                
                if args.verbose:
        
                    print(f"[{red}INFO{reset}]: {url} - Can't retrieve status code for this URL")
                
                else:
                    
                    pass





if __name__ == "__main__":
    
    check_essentials()
    
    load_urls()
    
