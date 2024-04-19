#!/usr/bin/env python3
import random 
import os  
from colorama import Fore,Back,Style
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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

def __version__():
    url = f"https://api.github.com/repos/sanjai-AK47/Subprober/releases/latest"
    try:
        response = requests.get(url, verify=True, timeout=10)
        if response.status_code == 200:
            data = response.json()
            latest = data.get('tag_name')
            return latest 
    except KeyboardInterrupt as e:
        print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        exit()
    except Exception as e:
        pass