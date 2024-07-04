import asyncio
from colorama import Fore, Style
import socket
import re
import aiodns

red = Fore.RED
blue = Fore.BLUE
white = Fore.WHITE
green = Fore.GREEN
yellow = Fore.YELLOW
bold = Style.BRIGHT
reset = Style.RESET_ALL



async def __getcname__(url, record, args):
    try:
        resolver = aiodns.DNSResolver()
        pattern = r'^(?:https?://)?((?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*)'
        extracted = re.match(pattern, url)
        domain = extracted.group(1)
        results = await resolver.query(domain, record)
        await asyncio.sleep(0.0000001)
        if results:
            cname = results.cname if results.cname else ""
            return cname
        return []
    except socket.gaierror as e:
        return []
    except aiodns.error.DNSError as e:
        return []
    except TimeoutError as e:
        return []
    except Exception as e:
        if args.secret_debug:
            print(f"Exception at dns: {e}, {type(e)}, {results}")
        
        
        
async def __getip__(url, record, args):
    try:
        resolver = aiodns.DNSResolver()
        pattern = r'^(?:https?://)?((?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*)'
        extracted = re.match(pattern, url)
        domain = extracted.group(1)
        results = await resolver.query(domain, record)
        await asyncio.sleep(0.0000001)
        if results:
            ips = [ip.host for ip in results]
            ips = ', '.join(ip for ip in ips)
            return ips
        return []
    except socket.gaierror as e:
        return []
    except aiodns.error.DNSError as e:
        return []
    except TimeoutError as e:
        return []
    except Exception as e:
        if args.secret_debug:
            print(f"Exception at dns: {e}, {type(e)}, {results}")