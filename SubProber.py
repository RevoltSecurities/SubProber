import argparse
from ast import Store
import concurrent.futures
import string
import requests
import os
import subprocess
import time
from colorama import Fore,Back,Style


red =  Fore.RED

green = Fore.GREEN

yellow = Fore.MAGENTA

cyan = Fore.CYAN

mixed = Fore.RED + Fore.BLUE

blue = Fore.BLUE

yellow = Fore.YELLOW

white = Fore.WHITE

reset = Style.RESET_ALL

#Lol You will Never understand this and it just for fun guys u can understand this easily



parser = argparse.ArgumentParser(description="Http status Finder")

parser.add_argument("-l", "--list", help="Path to the file that contains list of subdomains probe", type=str, required=True)

parser.add_argument("-o","--output", help="path to directory to save the output", type=str, required=True)

parser.add_argument("-v", "--verbose", help="Console the output to the terminal", action="store_true")

parser.add_argument("-c", "--concurrency", help="Concurrency level to probe", type=int, default=10)

args=parser.parse_args()


prober = ''' 

                 _____       _    ______          _               
                /  ___|     | |   | ___ \        | |              
                \ `--. _   _| |__ | |_/ / __ ___ | |__   ___ _ __ 
                 `--. \ | | | '_ \|  __/ '__/ _ \| '_ \ / _ \ '__|
                /\__/ / |_| | |_) | |  | | | (_) | |_) |  __/ |   
                \____/ \__,_|_.__/\_|  |_|  \___/|_.__/ \___|_|   
                                                  
                
                                                    Creator    : Sanjai Kumar

                                                    Tool       : SubProber

                                                    Description: Http Status Finder

                                                    github     : https://github.com/sanjai-AK47

                                                    version    : 1.0

                                                                                                    
                                                  '''

if args.list and args.output:

     print(f"{blue}{prober}{reset}")
     time.sleep(2)


if args.verbose:

    print(f"{green}[!]Verbose Enabled by User{reset}")

    time.sleep(1)
else:

    print(f"{red}[!]Verbose is not enabled{reset}")
    time.sleep(1)

if args.concurrency :

    print(f"{green}[!]Concurrency level: {args.concurrency}{reset}")
    time.sleep(1)

    if args.concurrency > 50:
         
         print(f"{red}[!]Warning giving concurrency level more than 50 cause inaccurate responses ,So carefully handle your concurrency level")
    else:
         pass
    


if args.output:
     
    output = args.output

    if os.path.exists(output):
          print(f"{green}[!]The output directory given by user is exist{reset}")
          time.sleep(1)
    else:
         print(f"{red}[!]The Given output directory doesn't exist")
         print(f"{green}[!]Creating directory to save the result")
         time.sleep(1)
         os.makedirs(output)
else:
     pass


def requestorator(url):

    response = None

    try:

        response = requests.get(url)

        status = response.status_code

        if args.verbose:
        
            if status == 200:
            
                 print(f"{green}[!]URL: {url} and status code: {status}{reset}")

                 writer(url,status)
        
            elif status == 302:

                 print(f"{cyan}[!]URL: {url} and status code: {status}{reset}")

                 writer(url,status)

            elif status == 301:

                 print(f"{blue}[!]URL: {url} and status code: {status}{reset}")

                 writer(url,status)
        
            elif status == 404:
             
                 print(f"{white}[!]URL: {url} and status code: {status}{reset}")

                 writer(url,status)

            elif status == 403:
             
                 print(f"{mixed}[!]URL: {url} and status code: {status}{reset}")

                 writer(url,status)
        
            elif status == 500:
             
                 print(f"{red}[!]URL: {url} and status code: {status}{reset}")

                 writer(url,status)
        
            elif status == 503:
             
                 print(f"{red}[!]URL: {url} and status code: {status}{reset}")

                 writer(url,status)

            elif status == 000:
             
                 print(f"{red}[!]URL: {url} and status code: {status}{reset}")

                 writer(url,status)
             
            else:
                 
                 print(f"{yellow}[!]URL: {url} and status code: {status}{reset}")

                 writer(url,status)
        else:
            pass

        return response
    
    except Exception as e:
         
        print(f"{red}[!]Something went wrong when giving request to this url: {url} {reset}")

        print(f"{green}[!]Reconnecting........{reset}")
        time.sleep(1)
        
        filename = os.path.join(output, "error_urls.txt")
        
        with open(filename, "a") as file:
             
             file.write(url+'\n')

        return None
    except KeyboardInterrupt as key:
          
          user = input(f"{red}[!]Do you want to stop the SubProber (yes/no): ")
          if user.lower() == "yes":
               
               print(f"{red}[!]User stopped the SubProber")
               exit()
          else:
               pass
       
         
         


if args.list:

    try:
        filename = args.list
        with open(filename,"r") as file:
            
            urls = file.read().splitlines()
            


    except Exception as e:

         print(f"{red}[!]Can't {args.list} read the file check the file path or file exist{reset}")
         exit()
else:

     print(f"{red}[!]Something went wrong on opening the {args.list}{reset}")
     exit()


def writer(url, status):
    if args.output:
        output = args.output

        if status == 200:
             filename = os.path.join(output, "200.txt")
             with open(filename, "a") as file:
             
                 file.write(url+'\n')

        elif status == 301:

             filename = os.path.join(output, "301.txt")
             with open(filename, "a") as file:
             
                 file.write(url+'\n')

        elif status == 302:

             filename = os.path.join(output, "302.txt")
             with open(filename, "a") as file:
             
                 file.write(url+'\n')

        elif status == 403:

             filename = os.path.join(output, "403.txt")

             with open(filename, "a") as file:
             
                 file.write(url+'\n')

        elif status == 404:

             filename = os.path.join(output, "404.txt")
             
             with open(filename, "a") as file:
             
                 file.write(url+'\n')
    
        elif status == 500:

             filename = os.path.join(output, "500.txt")

             with open(filename, "a") as file:
             
                 file.write(url+'\n')

        elif status == 503:

             filename = os.path.join(output, "503.txt")

             with open(filename, "a") as file:
             
                 file.write(url+'\n')

        elif status == 000:

             filename = os.path.join(output, "timeout_urls.txt")

             with open(filename, "a") as file:
             
                 file.write(url+'\n')

        else:

             filename = os.path.join(output, "others_urls.txt")
             with open(filename, "a") as file:
             
                 file.write(url+'\n')


               

def SubProber(url):

    urls = f"https://{url}"

    response=requestorator(urls)
    
    attempt = 0

    while response is None and attempt < 3:
         
        response = requestorator(urls)
 
        attempt+=1

    if attempt==3:
            
        print(f"{blue}[!]Reached Maximum connection for this url: {urls}")


with concurrent.futures.ThreadPoolExecutor(max_workers = args.concurrency) as executor:
     
     try:
     
        futures = [executor.submit(SubProber, url) for url in urls]
        concurrent.futures.wait(futures)
    
     except Exception as e: 
          
          print(f"{blue}[!]Something went wrong with the ThreadPoolExecutor: {e}{reset}")

     except KeyboardInterrupt as key:
          
          user = input(f"{red}[!]Do you want to stop the SubProber (yes/no): ")
          if user.lower() == "yes":
               
               print(f"{red}[!]User stopped the SubProber")
               exit()
          else:
               pass




