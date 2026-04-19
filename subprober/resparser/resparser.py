from subprober.dnsclient.dnsclient import AsyncDnsClient
from subprober.hash.hash import HashGen
from subprober.jarmscanner.jarmscanner import JarmScanner
from subprober.settings.settings import Settings
from subprober.websocketclient.websocketclient import AsyncWebSocketClient, WebSocketResult
from revoltlogger import Logger
from revoltutils.fileutils import FileUtils
from subprober.utils.utils import Utils
import warnings
from bs4 import XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning, BeautifulSoup, FeatureNotFound
import json
from colorama import Fore, Style, init
import random
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import aiohttp
init(autoreset=True)

class Resparser:
    def __init__(
            self,
            args: Settings,
            nameservers=["8.8.8.8", "1.1.1.1"],
            hashes=[]
    ) -> None:

        # Settings
        self.args = args
        self.nameservers = nameservers
        self.hashes = hashes

        # Logger
        self.logger = Logger()

        # Colors
        self.red = Fore.RED
        self.green = Fore.GREEN
        self.yellow = Fore.YELLOW
        self.blue = Fore.BLUE
        self.magenta = Fore.MAGENTA
        self.cyan = Fore.CYAN
        self.white = Fore.WHITE
        self.bold = Style.BRIGHT
        self.reset = Style.RESET_ALL
        self.color_list = [self.red, self.green, self.yellow, self.blue, self.magenta, self.cyan, self.white]
        self.random_color = random.choice(self.color_list)

        # Scanners
        self.utils = Utils()
        self.hasher = HashGen(self.hashes)
        self.jarmclient = JarmScanner(self.args.concurrency, self.args.timeout, self.args.verbose)
        self.dnsclient = AsyncDnsClient(nameservers=self.nameservers, max_retries=2,
                                        verbose=self.args.verbose)
        self.websocketclient = AsyncWebSocketClient(timeout=self.args.timeout,
                                                    verbose=self.args.verbose)
        self.saver = FileUtils()

    async def resparser(self, response: aiohttp.ClientResponse, url: str, elapsed_time: float = 0) -> Optional[Dict]:
        """
        Parse aiohttp ClientResponse object.

        Args:
            response: aiohttp.ClientResponse object (native, not wrapped)
            url: Original request URL
            elapsed_time: Request elapsed time in seconds (optional)

        Returns:
            Dictionary with parsed response data
        """
        results = {}
        try:
            results["timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            results["title"] = ""
            results["method"] = response.method.upper()
            results["url"] = str(url)

            parsed_url = urlparse(str(response.url))
            results["path"] = parsed_url.path or "/"

            results["status_code"] = response.status

            if hasattr(response, 'version'):
                results["http_version"] = f"HTTP/{response.version.major}.{response.version.minor}"
            else:
                results["http_version"] = "HTTP/1.1"

            results["response_reason"] = response.reason if hasattr(response, 'reason') else ''

            results["time"] = elapsed_time if elapsed_time > 0 else getattr(response, 'elapsed_seconds', 0)

            parsed = urlparse(str(response.url))
            results["host"] = parsed.hostname or ""
            results["scheme"] = parsed.scheme
            # Determine port
            if parsed.port:
                results["port"] = parsed.port
            elif parsed.scheme == 'https':
                results["port"] = 443
            elif parsed.scheme == 'http':
                results["port"] = 80
            else:
                results["port"] = 0

            results["final_url"] = str(response.url)

            if hasattr(response, 'cookies') and response.cookies:
                results["cookies"] = {key: morsel.value for key, morsel in response.cookies.items()}
            else:
                results["cookies"] = self._extract_cookies_from_headers(response.headers)
                cache_headers = {
                    "cache_control": response.headers.get("Cache-Control", ""),
                    "expires": response.headers.get("Expires", ""),
                    "etag": response.headers.get("ETag", ""),
                    "last_modified": response.headers.get("Last-Modified", ""),
                    "age": response.headers.get("Age", ""),
                    "pragma": response.headers.get("Pragma", ""),
                    "vary": response.headers.get("Vary", ""),
                }

                results["cache_headers"] = {k: v for k, v in cache_headers.items() if v}
                results["cache_headers_count"] = len(results["cache_headers"])

                # Cache control parsing
                cache_control = cache_headers["cache_control"]
                if cache_control:
                    results[
                        "is_cacheable"] = "no-store" not in cache_control.lower() and "no-cache" not in cache_control.lower()
                    results["cache_control_directives"] = [d.strip() for d in cache_control.split(",")]
                else:
                    results["is_cacheable"] = False
                    results["cache_control_directives"] = []

                cors_headers = {
                    "access_control_allow_origin": response.headers.get("Access-Control-Allow-Origin", ""),
                    "access_control_allow_credentials": response.headers.get("Access-Control-Allow-Credentials", ""),
                    "access_control_allow_methods": response.headers.get("Access-Control-Allow-Methods", ""),
                    "access_control_allow_headers": response.headers.get("Access-Control-Allow-Headers", ""),
                    "access_control_expose_headers": response.headers.get("Access-Control-Expose-Headers", ""),
                    "access_control_max_age": response.headers.get("Access-Control-Max-Age", ""),
                }

                results["cors_headers"] = {k: v for k, v in cors_headers.items() if v}
                results["has_cors"] = bool(results["cors_headers"])

            try:
                response_text = await response.text()
            except Exception as e:
                if self.args.verbose:
                    self.logger.warn(f"Failed to read response text: {e}")
                response_text = ""

            results["length"] = len(response_text)
            results["line_count"] = len(response_text.splitlines())
            results["word_count"] = len(response_text.split())
            results["body_preview"] = response_text[:100] if response_text else ""

            # Redirect history
            if (self.args.full_output or self.args.redirect_history) and self.args.json and self.args.allow_redirect:
                history = response.history if hasattr(response, 'history') else []
                results["response_history"] = [
                    {"url": str(r.url), "status_code": r.status}
                    for r in history
                ]

            if (self.args.full_output or self.args.redirect_urls) and self.args.json and self.args.allow_redirect:
                history = response.history if hasattr(response, 'history') else []
                results["redirected_urls"] = [str(r.url) for r in history] if history else []

            if (self.args.full_output or self.args.redirect_status_codes) and self.args.json and self.args.allow_redirect:
                history = response.history if hasattr(response, 'history') else []
                results["redirected_status_code"] = [r.status for r in history] if history else []

            # Request headers - aiohttp doesn't store request headers in response
            # You'll need to pass them separately or reconstruct
            if (self.args.full_output or self.args.request_headers) and self.args.json:
                if hasattr(response, 'request_info') and response.request_info:
                    results["request-headers"] = dict(response.request_info.headers) if hasattr(response.request_info,
                                                                                                'headers') else {}
                else:
                    results["request-headers"] = {}

            if (self.args.full_output or self.args.response_headers) and self.args.json:
                results["response-headers"] = dict(response.headers) if response.headers else {}

            # Extract title from HTML
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning)
                    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
                    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
                    soup = BeautifulSoup(response_text, "lxml")
                    title_tag = soup.title
                    title = title_tag.string if title_tag else ""
                    results["title"] = title
                    results["Title"] = title  # Keep both for compatibility
            except FeatureNotFound:
                if self.args.verbose:
                    self.logger.warn(
                        f"Looks like your beautifulsoup4, lxml, bs4 not in latest version, please update it")
            except Exception as e:
                if self.args.verbose:
                    self.logger.warn(f"Error parsing title: {e}")

            # Hash generation
            if self.args.hash or self.args.full_output:
                hashes = await self.hasher.gen(str(response_text))
                if hashes:
                    results["hash"] = hashes

            # JARM fingerprint
            if (self.args.jarm_fingerprint or self.args.full_output) and self.args.json:
                port = results.get("port", 443)
                jarmhash = await self.jarmclient.get_jarm_hash(url, port)
                if jarmhash:
                    results["jarm_fingerprint"] = jarmhash

            # DNS records
            if self.args.full_output or self.args.aaaa_records or self.args.json:
                aaaa = await self.dnsclient.resolve(url, "AAAA")
                if aaaa:
                    results["aaaa"] = aaaa

            if self.args.full_output or self.args.ipaddress or self.args.json:
                ips = await self.dnsclient.resolve(url, "A")
                if ips:
                    results["ipaddress"] = ips

            if self.args.full_output or self.args.cname or self.args.json:
                cname = await self.dnsclient.resolve(url, "CNAME")
                if cname:
                    results["cname"] = cname

            # Web server header
            webserver = response.headers.get("server") or response.headers.get("Server")
            if webserver:
                results["webserver"] = webserver

            # Content type
            content_type = response.headers.get("Content-type") or response.headers.get("content-type", "")
            if content_type:
                results["content_type"] = content_type.split(";")[0].strip()

            # WebSocket probe
            if self.args.websocket or self.args.json or self.args.full_output:
                websocket_response: WebSocketResult = await self.websocketclient.probe(url)
                if websocket_response.status == "allowed":
                    results["websocket_info"] = websocket_response.to_dict()
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occurred in the response handler module due to: {e}, {type(e)}, {url}")
        finally:
            return results

    def _extract_cookies_from_headers(self, headers) -> dict:
        """Extract cookies from Set-Cookie headers"""
        cookies = {}

        if hasattr(headers, 'getall'):
            set_cookie_headers = headers.getall('Set-Cookie', [])
        else:
            set_cookie = headers.get('Set-Cookie', '')
            set_cookie_headers = [set_cookie] if set_cookie else []

        for cookie_header in set_cookie_headers:
            parts = cookie_header.split(';')[0].split('=', 1)
            if len(parts) == 2:
                cookies[parts[0].strip()] = parts[1].strip()
        return cookies

    async def resultsparser(self, results: dict, url: str, filename: Optional[str | Path]):
        """
        Parse and format results for output with improved field mapping and logic.
        Compatible with the updated resparser field names.
        """
        try:
            if len(results) == 0:
                return

            if self.args.json:
                self.logger.stdinlog(json.dumps(results, ensure_ascii=False))
                if self.args.output:
                    await self.saver.json_write(filename, results, mode="a")
                return

            # Map resparser fields to display
            display_url = results.get('url', '')
            status_code = results.get('status_code', 0)
            title = results.get('title', results.get('Title', ''))
            server = results.get('webserver', '')
            content_type = results.get('content_type', '')
            word_count = results.get('word_count', 0)
            line_count = results.get('line_count', 0)
            length = results.get('length', 0)
            final_url = results.get('final_url', '')
            http_version = results.get('http_version', '')
            response_reason = results.get('response_reason', '')
            response_time = results.get('time', 0)
            body_preview = results.get('body_preview', '')
            method = results.get('method', 'GET')

            # DNS records
            ip_addresses = results.get('ipaddress', [])
            cname_records = results.get('cname', [])
            aaaa_records = results.get('aaaa', [])

            # Hash and fingerprint data
            hash_data = results.get('hash', {})
            jarm_data = results.get('jarm_fingerprint', '')
            websocket_info = results.get('websocket_info', {})
            websocket_status = websocket_info.get('status', 'N/A') if websocket_info else 'N/A'

            # Build formatted output with colors
            if not self.args.no_color:
                # URL (always displayed)
                Url = f"{self.bold}{self.white}{display_url}{self.reset}"

                # Status Code with color coding
                if self.args.status_code:
                    if 200 <= status_code <= 299:
                        StatusCode = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.green}{status_code}{self.reset}{self.bold}{self.white}]{self.reset}"
                    elif 300 <= status_code <= 399:
                        StatusCode = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.yellow}{status_code}{self.reset}{self.bold}{self.white}]{self.reset}"
                    elif 400 <= status_code <= 499:
                        StatusCode = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.red}{status_code}{self.reset}{self.bold}{self.white}]{self.reset}"
                    elif 500 <= status_code <= 599:
                        StatusCode = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.red}{status_code}{self.reset}{self.bold}{self.white}]{self.reset}"
                    else:
                        StatusCode = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.white}{status_code}{self.reset}{self.bold}{self.white}]{self.reset}"
                else:
                    StatusCode = ""

                # Optional fields
                Method = f" {self.bold}{self.white}[{self.reset}{self.random_color}{method}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.display_method else ""
                Title = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.cyan}{title}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.title and title else ""
                Server = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.magenta}{server}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.server and server else ""
                ContentType = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.yellow}{content_type}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.application_type and content_type else ""

                # Metrics
                WordCount = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.green}{word_count}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.word_count else ""
                LineCount = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.red}{line_count}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.line_count else ""
                Length = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.green}{length}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.content_length else ""

                # Redirect info
                Location = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.magenta}{final_url}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.location and self.args.allow_redirect and final_url != display_url else ""

                # DNS records
                IpAddress = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.yellow}{','.join(map(str, ip_addresses))}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.ipaddress and ip_addresses else ""
                Cname = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.green}{','.join(map(str, cname_records))}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.cname and cname_records else ""
                AAAA = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.cyan}{','.join(map(str, aaaa_records))}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.aaaa_records and aaaa_records else ""

                # HTTP details
                HttpVersion = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.blue}{http_version}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.http_version and http_version else ""
                HttpReason = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.magenta}{response_reason}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.http_reason and response_reason else ""
                ResponseTime = f" {self.bold}{self.white}[{self.reset}{self.random_color}{response_time}s{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.response_time else ""

                # Security/Fingerprinting
                Jarm = f" {self.bold}{self.white}[{self.reset}{self.bold}{self.magenta}{jarm_data}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.jarm_fingerprint and jarm_data else ""
                WebSocket = f" {self.bold}{self.white}[{self.reset}{self.random_color}ws:{websocket_status}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.websocket else ""

                # Hash values
                Hash = ""
                if self.args.hash and hash_data:
                    hash_values = ','.join(f"{k}:{v}" for k, v in hash_data.items())
                    Hash = f" {self.bold}{self.white}[{self.reset}{self.random_color}{hash_values}{self.reset}{self.bold}{self.white}]{self.reset}"

                # Body preview
                BodyPreview = f" {self.bold}{self.white}[{self.reset}{self.random_color}{body_preview}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.body_preview and body_preview else ""

            else:
                # No color output
                Url = display_url
                StatusCode = f" [{status_code}]" if self.args.status_code else ""
                Method = f" [{method}]" if self.args.display_method else ""
                Title = f" [{title}]" if self.args.title and title else ""
                Server = f" [{server}]" if self.args.server and server else ""
                ContentType = f" [{content_type}]" if self.args.application_type and content_type else ""
                WordCount = f" [{word_count}]" if self.args.word_count else ""
                LineCount = f" [{line_count}]" if self.args.line_count else ""
                Length = f" [{length}]" if self.args.content_length else ""
                Location = f" [{final_url}]" if self.args.location and self.args.allow_redirect and final_url != display_url else ""
                IpAddress = f" [{','.join(map(str, ip_addresses))}]" if self.args.ipaddress and ip_addresses else ""
                Cname = f" [{','.join(map(str, cname_records))}]" if self.args.cname and cname_records else ""
                AAAA = f" [{','.join(map(str, aaaa_records))}]" if self.args.aaaa_records and aaaa_records else ""
                HttpVersion = f" [{http_version}]" if self.args.http_version and http_version else ""
                HttpReason = f" [{response_reason}]" if self.args.http_reason and response_reason else ""
                ResponseTime = f" [{response_time}s]" if self.args.response_time else ""
                Jarm = f" [{jarm_data}]" if self.args.jarm_fingerprint and jarm_data else ""
                WebSocket = f" [ws:{websocket_status}]" if self.args.websocket else ""
                Hash = f" [{','.join(f'{k}:{v}' for k, v in hash_data.items())}]" if self.args.hash and hash_data else ""
                BodyPreview = f" [{body_preview}]" if self.args.body_preview and body_preview else ""

            # Build final output string
            output = f"{Url}{StatusCode}{Method}{Title}{Server}{ContentType}{WordCount}{LineCount}{Length}{Location}{IpAddress}{Cname}{AAAA}{HttpVersion}{HttpReason}{ResponseTime}{Jarm}{WebSocket}{Hash}{BodyPreview}"
            self.logger.stdinlog(output)
            if self.args.output:
                await self.saver.write(filename, f"{output}\n", "a")
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occurred in resultsparser for URL: '{url}' - {type(e).__name__}: {e}")