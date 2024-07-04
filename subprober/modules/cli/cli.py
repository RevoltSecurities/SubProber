#!/usr/bin/env python3
from colorama import Fore,Style
import argparse
import time as t
import random

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

def __cli__():
    
    try:
        parser =  argparse.ArgumentParser(add_help=False,usage=argparse.SUPPRESS,exit_on_error=False )
        parser.add_argument("-f", "--filename",  type=str)
        parser.add_argument("-h", "--help", action="store_true")
        parser.add_argument("-u", "--url",  type=str )
        parser.add_argument("-o", "--output", type=str)
        parser.add_argument("-c", "--concurrency", type=int, default=100)
        parser.add_argument("-tl", "--title", action="store_true")
        parser.add_argument("-to", "--timeout", type=int, default=10)
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
        parser.add_argument("-X", "--method", type=str, choices=["get", "post", "head", "put", "delete", "patch", "trace", "connect", "options"], default="get")
        parser.add_argument("-H", "--header", action="append")
        parser.add_argument("-sc", "--status-code", action="store_true")
        parser.add_argument("-ra", "--random-agent", action="store_true")
        parser.add_argument("-ss", "--screenshot", action="store_true")
        parser.add_argument("-st", "--screenshot-timeout", type=int, default=10)
        parser.add_argument("-bt", "--browser-type", type=str, choices=["firefox", "chrome"], default="chrome")
        parser.add_argument("-oD", "--output-directory", type=str)
        parser.add_argument("-ip", "--ipaddress", action="store_true")
        parser.add_argument("-cn", "--cname", action="store_true")
        parser.add_argument("-maxr", "--max-redirection", type=int, default=10)
        parser.add_argument("-sup", "--show-updates", action="store_true")
        parser.add_argument("-http2", "--http2", action="store_true")
        parser.add_argument("-htv", "--http-version", action="store_true")
        parser.add_argument("-hrs", "--http-reason", action="store_true")
        parser.add_argument("-jarm", "--jarm-fingerprint", action="store_true")
        parser.add_argument("-sd", "--secret-debug", action="store_true") # this isn't for you!
        global args 
        return parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Please use the command for more infromation:{reset} {bold}{blue}Subprober -h {e}{reset}")
        quit()
    except argparse.ArgumentTypeError as e:
        print(f"[{bold}{blue}INFO{reset}]: {bold}{white}Please use the command for more infromation:{reset} {bold}{blue}Subprober -h {e}{reset}")
        quit()
    except KeyboardInterrupt as e:
        print(f"\n[{bold}{blue}INFO{reset}]: {bold}{white}Subprober exits..{reset}")
        quit()
    except Exception as e:
        pass