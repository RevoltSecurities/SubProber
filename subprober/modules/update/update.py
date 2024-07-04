import requests
from colorama import Fore, Style
import subprocess
import os
from rich.console import Console
from rich.markdown import Markdown

console = Console()
bold =Style.BRIGHT
blue = Fore.BLUE
red  = Fore.RED
white = Fore.WHITE
reset = Style.RESET_ALL

def __getzip__(): 
    try:
        url = "https://api.github.com/repos/sanjai-AK47/Subprober/releases/latest"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()['zipball_url']
        else:
            print(f"[{bold}{red}ALERT{reset}]: {bold}{white}Hey Update Failed for Subprober, Please try to update the Subprober manually{reset}")
            quit()
    except Exception as e:
        pass
    

def __launch__(url,config):
    try:
        response = requests.get(url, timeout=20, stream=True)
        filepath = f"{config}/Subprober.zip"
        if response.status_code == 200:
            print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Downloading Subprober latest version...{reset}")
            
            with open(f"{filepath}", "wb") as streamw:
                for data in response.iter_content():
                    if data:
                        streamw.write(data)
            try:
                subprocess.run(["pip", "install", f"{filepath}"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                os.remove(filepath)
                            
            except Exception as e:
                print(f"[{bold}{red}ALERT{reset}]: {bold}{white}Update Failed for Subprober, Please try to update the Subprober manually{reset}")
                os.remove(filepath)
                quit()
        else:
            
            print(f"[{bold}{red}ALERT{reset}]: {bold}{white}Update Failed for Subprober, Please try to update the Subprober manually{reset}")
            quit()
            
    except Exception as e:
        
        pass

def __updatelog__(config):
    try:
        
        url = f"https://raw.githubusercontent.com/sanjai-AK47/Subprober/main/subprober/updatelog.MD"
        
        response = requests.get(url, timeout=20, stream=True)
        
        if response.status_code == 200:
            
            loader = response.text
            
            console.print(Markdown(loader))
            
        else:
            print(f"[{bold}{red}ALERT{reset}]: {bold}{white}Hey  unable to fetch update logs so please visit here --> https://github.com/sanjai-AK47/Subprober{reset}")
            quit()
    except Exception as e:
        pass
    