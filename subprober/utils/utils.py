import asyncio
from urllib.parse import urlparse, urlunparse, urljoin
from subprober.logger.logger import Logger 
import aiofiles
from fake_useragent import UserAgent
from itertools import islice
from requests.cookies import RequestsCookieJar
from urllib.parse import urlparse 
import random
import string

class Utils:
    def __init__(self):
        self.logger = Logger()
        
    @staticmethod
    def extract_cookies(cookie_jar: RequestsCookieJar) -> list[dict]:
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

    async def Reader(self, file: str, args) -> list[str]:
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
            self.logger.warn(f"{file} have insufficient permission to read")
            exit(1)
        except FileNotFoundError:
            self.logger.warn(f"{file}: no such file or directory exist")
            exit(1)
        except Exception as e:
            self.logger.warn(f"Exception occured in return reader due to: {e}, {type(e)}")
            exit(1)

    async def permissions(self, filename: str) -> bool:
        try:
            async with aiofiles.open(filename, mode='a') as file:
                pass
            return True
        except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
        except PermissionError:
            self.logger.warn(f"{filename} have insufficient permission to write")
            exit(1)
        except Exception as e:
            self.logger.warn(f"Exception occured in util permission checker due to: {e}, {type(e)}")
            return False 

    @staticmethod
    def GetDomain(url: str) -> str:
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.hostname
            return domain if domain is not None else "" 
        except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
        except Exception:
            pass
        return ""

    @staticmethod
    def extractor(data: str) -> list[str]:
        extracted = []
        final = data.split(",")
        extracted.extend([hash_val.strip() for hash_val in final]) 
        return extracted 

    @staticmethod
    def Useragents() -> str:
        return UserAgent().random

    @staticmethod
    def chunker(data, size: int = 100000):
        it = iter(data)
        while chunk := list(islice(it, size)):
            yield chunk

    @staticmethod
    def string_to_str_list(words: str | None) -> list[str] | None:
        if words is None:
            return []
        values = [str(word).strip() for word in words.split(",")] # Added .strip()
        return values

    @staticmethod
    def string_to_int_list(words: str | None) -> list[int] | None:
        if words is None:
            return None
        values = [int(num.strip()) for num in words.split(",")]
        return values

    @staticmethod
    def validate_url(url:str, http_include=False) -> list[str]:
        validated_urls = []
        if url.startswith("http://") or url.startswith("https://"):
            validated_urls.append(url)
        else:
            validated_urls.append(f"https://{url}")
            if not http_include:
                validated_urls.append(f"http://{url}")
        return list(set(validated_urls))
    

    @staticmethod
    def add_ports_to_urls(urls, ports):
        if ports is None:
            return urls
        result_urls = []
        for url in urls:
            parsed_url = urlparse(url)
            if ':' in parsed_url.netloc:
                netloc_without_port = parsed_url.netloc.split(':')[0]
            else:
                netloc_without_port = parsed_url.netloc
            for port in ports:
                new_netloc = f"{netloc_without_port}:{port}"
                new_url_parts = parsed_url._replace(netloc=new_netloc)
                result_urls.append(urlunparse(new_url_parts))
        return result_urls


    @staticmethod
    def add_paths_to_urls(urls: list[str], paths=None)-> list[str]:
        if not paths:
            return urls
        urls_with_paths = []
        for url in urls:
            for path in paths:
                urls_with_paths.append(urljoin(url, path))
        return urls_with_paths
    
    @staticmethod
    def generate_random() -> str:
        return ''.join(random.choices(string.ascii_letters, k=6))