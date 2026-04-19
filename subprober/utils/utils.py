import asyncio
from urllib.parse import urlunparse, urljoin
from requests.cookies import RequestsCookieJar
from urllib.parse import urlparse
import random
import string
from typing import List, Optional,Dict,Any
from revoltlogger import Logger


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
    def validate_url(url: str, http_include=False) -> str:
        if url.startswith("http://") or url.startswith("https://"):
            return url
        else:
            return f"https://{url}"

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
    def add_paths_to_urls(urls: list[str], paths=None) -> list[str]:
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

    @staticmethod
    def validate_and_expand_urls(
            raw_url: str,
            ports: Optional[List[int]] = None,
            paths: Optional[List[str]] = None,
    ) -> List[str]:

        if not raw_url:
            return []

        # Step 1: Handle scheme
        base_urls: List[str] = []
        if raw_url.startswith("http://") or raw_url.startswith("https://"):
            base_urls.append(raw_url)
        else:
            base_urls.append(f"https://{raw_url}")

        expanded_urls: List[str] = []

        if ports:
            urls_with_ports = set()
            for url in base_urls:
                parsed_url = urlparse(url)
                netloc_without_port = parsed_url.netloc.split(':')[0]

                for port in ports:
                    # Construct new netloc with the current port
                    new_netloc = f"{netloc_without_port}:{port}"
                    new_url_parts = parsed_url._replace(netloc=new_netloc)
                    urls_with_ports.add(urlunparse(new_url_parts))
            expanded_urls = list(urls_with_ports)
        else:
            expanded_urls = base_urls  # If no ports, just use the base URLs

        final_urls: List[str] = []

        if paths:
            urls_with_paths = set()  # Use a set for uniqueness
            for url in expanded_urls:
                for path in paths:
                    urls_with_paths.add(urljoin(url, path))
            final_urls = list(urls_with_paths)
        else:
            final_urls = expanded_urls
        return list(set(final_urls))


class InputValidator:
    """Lightweight input validator"""

    @staticmethod
    def is_ipv4(host: str) -> bool:
        try:
            parts = host.split('.')
            if len(parts) != 4:
                return False
            return all(0 <= int(part) <= 255 for part in parts)
        except:
            return False

    @staticmethod
    def is_ipv6(host: str) -> bool:
        try:
            import ipaddress
            ipaddress.IPv6Address(host)
            return True
        except:
            return False

    @staticmethod
    def is_cidr(host: str) -> bool:
        try:
            import ipaddress
            return '/' in host and ipaddress.ip_network(host, strict=False) is not None
        except:
            return False

    @staticmethod
    def is_url(host: str) -> bool:
        return host.startswith(('http://', 'https://'))

    @staticmethod
    def is_domain(host: str) -> bool:
        if '.' not in host or ' ' in host:
            return False
        if InputValidator.is_ipv4(host) or InputValidator.is_ipv6(host):
            return False
        if InputValidator.is_cidr(host):
            return False
        return True

    @staticmethod
    def normalize(host: str) -> str:
        host = host.strip()
        if not host.startswith(('http://', 'https://')) and host.endswith('/'):
            host = host.rstrip('/')
        return host
