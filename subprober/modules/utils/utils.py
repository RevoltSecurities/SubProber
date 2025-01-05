import asyncio
import os
from urllib.parse import urlparse,urlunparse, urljoin
from subprober.modules.logger.logger import logger
import aiofiles
from fake_useragent import UserAgent
from itertools import islice
from requests.cookies import RequestsCookieJar
from urllib.parse import urlparse

def extract_cookies(cookie_jar):
    formatted_cookies = []
    if cookie_jar:
        for cookie in cookie_jar:
            cookie_data = {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "expires": cookie.expires,
                "secure": cookie.secure,
                "http_only": cookie.has_nonstandard_attr('HttpOnly')
            }
            formatted_cookies.append(cookie_data)
    return formatted_cookies

async def Reader(file: str, args) -> list[str]:
    try:
        content = []
        async with aiofiles.open(file, "r") as streamr:
            data = await streamr.read()
            data = data.splitlines()
        for d in data:
            content.append(d)
        return content
    except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
    except PermissionError:
        logger(f"{file} have insufficient permission to read", "warn", args.no_color)
        exit(1)
    except FileNotFoundError:
        logger(f"{file}: no such file or directory exist", "error", args.no_color)
        exit(1)
    except Exception as e:
        logger(f"Exception occured in return reader due to: {e}, {type(e)}", "warn", args.no_color)
        exit(1)

async def permissions(filename, args) -> bool:
    try:
        async with aiofiles.open(filename, mode='a') as file:
            pass
        return True
    except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
    except PermissionError:
        logger(f"{filename} have insufficient permission to write", "warn", args.no_color)
        exit(1)
    except Exception as e:
        logger(f"Exception occured in util permission checker due to: {e}, {type(e)}", "warn", args.no_color)
        

def GetDomain(url) -> str:
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.hostname
        return domain
    except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
    except Exception as e:
        pass
    
def extractor(data):
    extracted = []
    final = data.split(",")
    extracted.extend([hash for hash in final])
    
def Useragents() -> str:
    return UserAgent().random

def chunker(data, size=100000):
    it = iter(data)
    while chunk := list(islice(it, size)):
        yield chunk
        
def string_to_str_list(words) -> list[str] | None:
    if words is None:
        return None
    values = [str(word) for word in words.split(",")]
    return values

def string_to_int_list(words) -> list[int] | None:
    if words is None:
        return None
    values = [int(num) for num in words.split(",")]
    return values


def validate_urls(urls: list[str], http_include=False) -> list[str]:
    validated_urls = []
    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme in ("http", "https"):
            validated_urls.append(url)
        else:
            validated_urls.append(f"https://{url}")
            if not http_include:
                validated_urls.append(f"http://{url}")
    return list(set(validated_urls))

def add_ports_to_urls(urls: list[str], ports=None) -> list[str]:
    urls_with_ports = []
    for url in urls:
        parsed = urlparse(url)
        scheme = parsed.scheme
        
        if ports:
            for port in ports:
                new_netloc = f"{parsed.hostname}:{port}"
                urls_with_ports.append(urlunparse(parsed._replace(netloc=new_netloc)))
        else: 
            default_port = 80 if scheme == "http" else 443
            new_netloc = f"{parsed.hostname}:{default_port}"
            urls_with_ports.append(urlunparse(parsed._replace(netloc=new_netloc)))
    return urls_with_ports


def add_paths_to_urls(urls: list[str], paths=None)-> list[str]:
    if not paths:
        return urls
    urls_with_paths = []
    for url in urls:
        for path in paths:
            urls_with_paths.append(urljoin(url, path))
    return urls_with_paths