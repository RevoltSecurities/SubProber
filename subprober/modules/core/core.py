import asyncio
import httpx
import warnings
import argparse
import aiodns
from asynciolimiter import Limiter
from datetime import datetime
import json
from httpx import AsyncHTTPTransport
from alive_progress import alive_bar
from bs4 import  XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning, BeautifulSoup, FeatureNotFound
from subprober.modules.logger.logger import logger, stdinlog, bold,white,green,blue,cyan,magenta,yellow,red,reset,random_color
from subprober.modules.websocket.websocket import AsyncWebsocket
from subprober.modules.dns.dns import dns
from subprober.modules.jarmhash.jarmhash import jarmhash
from subprober.modules.hash.hash import Hashgen
from subprober.modules.utils.utils import Useragents, chunker,extract_cookies
from subprober.modules.tls.tls import tlsinfo
from subprober.modules.filters.filters import *
from subprober.modules.matchers.matchers import *
from subprober.modules.screenshot.screenshot import Headless
from subprober.modules.save.save import save

class Subprober:
    def __init__(
        self, 
        urls: list[str], 
        args: argparse.ArgumentParser.parse_args,
        nameservers=["8.8.8.8", "1.1.1.1"],
        hashes = [],
        mc = None,
        fc = None,
        mcr = None,
        fcr = None,
        mpt = None,
        fpt = None,
        ms = None,
        fs = None,
        mrg = None,
        frg = None,
        mrt = None,
        frt = None,
        mlc = None,
        flc = None,
        mwc = None,
        fwc = None,
        ml = None,
        fl = None,
        ) -> None:
        
        self.urls = urls
        self.args = args
        self.semaphore = asyncio.Semaphore(self.args.concurrency)
        self.scsem = asyncio.Semaphore(self.args.screenshot_threads)
        self.nameservers = nameservers
        self.loop = asyncio.get_event_loop()
        self.resolver = aiodns.DNSResolver(nameservers=self.nameservers, rotate=True, loop=self.loop)
        self.rate_limit = Limiter(rate=self.args.rate_limit/1)
        self.hashes = hashes
        self.mc = mc
        self.fc = fc
        self.mcr = mcr
        self.fcr = fcr
        self.mpt = mpt
        self.fpt = fpt
        self.ms = ms
        self.fs = fs
        self.mrg = mrg
        self.frg = frg
        self.mrt = mrt
        self.frt = frt
        self.mlc = mlc
        self.flc = flc
        self.mwc = mwc
        self.fwc = fwc
        self.ml = ml
        self.fl = fl
        self.screenshots = None
        
    async def request(self, method: str, url: str, client: httpx.AsyncClient) -> httpx.Response:
        try:
            await self.rate_limit.wait()
            headers = {}
            if self.args.header:
                for header in self.args.header:
                    name, value = header.split(':', 1)
                    headers[name.strip()] = value.strip()
            headers["User-Agent"] = Useragents() if self.args.random_agent else "git+Subprober/V2.XD"
            if self.args.sni_hostname:
                extensions = {"sni_hostname": f"{self.args.sni_hostname}"}
            else:
                extensions = None
            response = await client.request(method.upper(), url,headers=headers,follow_redirects=self.args.allow_redirect, extensions=extensions)
            return response
        except (httpx.ConnectError, httpx.ConnectTimeout):
            pass
        except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
        except Exception as e:
            if self.args.verbose:
                logger(f"Exception occured in the subprober request module due to: {e}, {type(e)}, {url}", "warn", self.args.no_color)
            return None
        
    async def responsed(self, response: httpx.Response, url: str) -> dict:
        try:
            network_streams = response.extensions.get("network_stream")
            server_addr = network_streams.get_extra_info("server_addr") if network_streams else None
            results = {}
            results["Title"] = ""
            results["Timestamp"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            results["Url"] = str(url)
            results["FinalUrl"] = str(response.url)
            results["IsRedirect"] = response.has_redirect_location
            
            if self.args.full_output or self.args.redirect_history and self.args.json and self.args.allow_redirect:
                results["RedirectHistory"] = [{"url": str(r.url), "status_code": r.status_code} for r in response.history]
                
            if self.args.full_output or self.args.redirect_urls and self.args.json and self.args.allow_redirect:
                results["RedirectedUrls"] = [str(redirect.url) for redirect in response.history] if response.history else []
                
            if self.args.full_output or self.args.redirect_status_codes and self.args.json and self.args.allow_redirect:
                results["RedirectedStatusCode"] = [int(redirect.status_code) for redirect in response.history] if response.history else []
                
            results["HttpVersion"] = response.http_version 
            results["ResponseReason"] = response.reason_phrase 
            results["StatusCode"] = response.status_code
            results["ResponseTime"] = response.elapsed.total_seconds()
            
            results["Method"] = response.request.method
            results["Host"] = str(response.request.url.host) if response.request.url.host else ""
            results["Port"] = str(response.request.url.port) if response.request.url.port else ""
            results["ServerAddress"] = str([server_addr[0]]) if server_addr is not None else ""
            results["ServerPort"] = str([server_addr[1]]) if server_addr is not None else ""
            
            if self.args.full_output or self.args.request_headers and self.args.json:
                results["RequestHeaders"] = dict(response.request.headers) if response.request.headers else {}
                
            if self.args.full_output or self.args.response_headers and self.args.json:
                results["ResponseHeaders"] = dict(response.headers) if response.headers else {}
                
            results["Cookies"] = extract_cookies(response.cookies.jar) if response.cookies.jar else []
            results["Length"] = len(response.text) 
            results["LineCount"] = len(response.text.splitlines()) 
            results["WordCount"] = len(response.text.split()) 
            results["BodyPreview"] = response.text[:100] if response.text else ""
            
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=UserWarning)
                    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
                    warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)
                    soup = BeautifulSoup(response.text, "lxml")
                    title_tag = soup.title
                    title = title_tag.string if title_tag else ""
                    results["Title"] = title
            except FeatureNotFound:
                if self.args.verbose:
                    logger(f"Looks like your beautifulsoup4, lxml, bs4 not in latest version, please update it", "warn", self.args.no_color)
                results["Title"] = ""
                
            if self.args.hash:
                hashes= await Hashgen(response.text, self.hashes, self.args)
                results["Hash"] = hashes if hashes else {}
                
            if self.args.jarm_fingerprint:
                jarmhashes = await jarmhash(url, self.args)
                results["JarmHash"] = jarmhashes

            if self.args.full_output or self.args.cname:
                cname = await dns(self.resolver, url, "CNAME", self.args)
                results["Cname"] = cname

            if self.args.full_output or self.args.ipaddress:
                ips = await dns(self.resolver, url, "A", self.args)
                results["A"] = ips

            if self.args.full_output or self.args.aaa_records:
                aaaa = await dns(self.resolver, url, "AAAA", self.args)
                results["AAAA"] = aaaa
            
            results["Server"] = response.headers.get("server", "")
            
            content_type = response.headers.get("Content-Type", "")
            if content_type:
                content_type = content_type.split(";")[0].strip()
                results["ContentType"] = content_type
            else:
                results["ContentType"] = ""
            
            
            if self.args.websocket:
                websocket = await AsyncWebsocket(url, self.args)
                results["Websockets"] = websocket
            
                
            if self.args.full_output or self.args.tls and self.args.json:
                tls = await tlsinfo(self.args, network_streams)
                results["TLS"] = tls
            
            if await match_by_code(response, self.mc) and \
                await match_code_range(response, self.mcr) and\
                await match_url_path_contains(response, self.mpt)and\
                await match_word_body(response, self.ms) and \
                await match_by_regex(response,self.mrg)and \
                await match_response_time(response, self.mrt)and \
                await filter_by_code(response, self.fc) and \
                await filter_code_range(response, self.fcr) and \
                await filter_url_path_contains(response, self.fpt) and \
                await filter_word_body(response, self.fs) and \
                await filter_by_regex(response, self.frg) and \
                await filter_response_time(response, self.frt) and \
                await match_by_ints(response.status_code, self.ml) and \
                await filter_by_ints(response.status_code, self.fl) and \
                await match_by_ints(response.status_code, self.mlc) and \
                await filter_by_ints(response.status_code, self.flc) and \
                await match_by_ints(response.status_code, self.mwc) and \
                await filter_by_ints(response.status_code, self.fwc):

                if self.args.screenshot:
                    await self.scsem.acquire()
                    await self.screenshots.run(results["Url"],results=results)
            else:
                results =  None
                
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger("CTRL+C Pressed!", "debug", self.args.no_color)
            exit(1)
        except Exception as e:
            if self.args.verbose:
                logger(f"Exception occured in the response handler module due to: {e}, {type(e)}, {url}", "warn", self.args.no_color)
        finally:
            if self.args.screenshot:
                self.scsem.release()
            return results
        
            
    async def manage(self, url, method, bar, session: httpx.AsyncClient) -> None:
        try:
            self.semaphore.release()
            await asyncio.sleep(self.args.delay)
            response = await self.request(method, url,session)
            
            if response is None:
                return
            results = await self.responsed(response, url)
            
            if results is None:
                return
            
            if self.args.json:
                stdinlog(json.dumps(results, ensure_ascii=False))
            
                if self.args.output:
                    await save(self.args.output, results, self.args.json, self.args.no_color)
                    
            else:
                
                if not self.args.no_color:
                    Url = f"{bold}{white}{results["Url"]}"
                    
                    sc = results["StatusCode"]
                    statuscode = sc if self.args.status_code else ""
                    
                    if self.args.status_code:
                        if statuscode >=200 and statuscode <=299:
                            StatusCode = f"{bold}{white}[{reset}{bold}{bold}{green}{statuscode}{reset}{bold}{white}]{reset}"
                        elif statuscode >=300 and statuscode <=399:
                            StatusCode = f"{bold}{white}[{reset}{bold}{bold}{yellow}{statuscode}{reset}{bold}{white}]{reset}"
                        else:
                            StatusCode = f"{bold}{white}[{reset}{bold}{red}{statuscode}{reset}{bold}{white}]{reset}"
                    else:
                        StatusCode = ""
                    
                    Jarm = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{magenta}{results["JarmHash"]}{reset}{bold}{white}]{reset}" if self.args.jarm_fingerprint else ""
                    Title = f"{bold}{white}[{reset}{bold}{cyan}{results["Title"]}{reset}{bold}{white}]{reset}" if self.args.title else ""
                    Server = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{magenta}{results["Server"]}{reset}{bold}{white}]{reset}" if self.args.server else ""
                    Wc  = f"{bold}{white}[{reset}{bold}{green}{results["WordCount"]}{reset}{bold}{white}]{reset}" if self.args.word_count else ""
                    Lc  = f"{bold}{white}[{reset}{bold}{red}{results["LineCount"]}{reset}{bold}{white}]{reset}" if self.args.line_count else ""
                    Lt  = f"{bold}{white}[{reset}{bold}{green}{results["Length"]}{reset}{bold}{white}]{reset}" if self.args.content_length else ""
                    Lo  = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{magenta}{results["FinalUrl"]}{reset}{bold}{white}]{reset}" if self.args.location and self.args.allow_redirect else ""
                    Apt = f"{bold}{white}[{reset}{bold}{yellow}{results["ContentType"]}{reset}{bold}{white}]{reset}" if self.args.application_type else ""
                    A   = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{yellow}{",".join(map(str, results["A"]))}{reset}{bold}{white}]{reset}" if self.args.ipaddress else "" 
                    Cn  = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{green}{",".join(map(str, results["Cname"]))}{reset}{bold}{white}]{reset}" if self.args.cname else ""
                    AAA = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{cyan}{",".join(map(str, results["AAAA"]))}{reset}{bold}{white}]{reset}" if self.args.aaa_records else ""
                    Htv = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{blue}{results["HttpVersion"]}{reset}{bold}{white}]{reset}" if self.args.http_version else ""
                    Htr = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{magenta}{results["ResponseReason"]}{reset}{bold}{white}]{reset}" if self.args.http_reason else ""
                    Rpt = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{random_color}{results["ResponseTime"]}{reset}{bold}{white}]{reset}" if self.args.response_time else ""
                    Wss = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{random_color}websocket: {results["Websockets"]}{reset}{bold}{white}]{reset}" if self.args.websocket else ""
                    Hsh = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{random_color}{",".join(map(str, results["Hash"].values()))}{reset}{bold}{white}]{reset}" if self.args.hash else ""
                    Dmt = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{random_color}{results["Method"]}{reset}{bold}{white}]{reset}" if self.args.display_method else ""
                    Bpv = f"{bold}{white}[{reset}{bold}{white}{reset}{bold}{random_color}{results["BodyPreview"]}{reset}{bold}{white}]{reset}" if self.args.body_preview else ""
                else:
                    Url = f"{results['Url']}"
                    StatusCode = f"[{results["StatusCode"]}]" if self.args.status_code else ""
                    Jarm = f"[{results['JarmHash']}]" if self.args.jarm_fingerprint else ""
                    Title = f"[{results['Title']}]" if self.args.title else ""
                    Server = f"[{results['Server']}]" if self.args.server else ""
                    
                    Wc = f"[{results['WordCount']}]" if self.args.word_count else ""
                    Lc = f"[{results['LineCount']}]" if self.args.line_count else ""
                    Lt = f"[{results['Length']}]" if self.args.content_length else ""
                    Lo = f"[{results['FinalUrl']}]" if self.args.location and self.args.allow_redirect else ""
                    Apt = f"[{results['ContentType']}]" if self.args.application_type else ""
                    A = f"[{','.join(map(str, results['A']))}]" if self.args.ipaddress else ""
                    Cn = f"[{','.join(map(str, results['Cname']))}]" if self.args.cname else ""
                    AAA = f"[{','.join(map(str, results['AAAA']))}]" if self.args.aaa_records else ""
                    Htv = f"[{results['HttpVersion']}]" if self.args.http_version else ""
                    Htr = f"[{results['ResponseReason']}]" if self.args.http_reason else ""
                    Rpt = f"[{results['ResponseTime']}]" if self.args.response_time else ""
                    Wss = f"[websocket: {results['Websockets']}]" if self.args.websocket else ""
                    Hsh = f"[{','.join(map(str, results['Hash'].values()))}]" if self.args.hash else ""
                    Dmt = f"[{results['Method']}]" if self.args.display_method else ""
                    Bpv = f"[{results['BodyPreview']}]" if self.args.body_preview else ""
                
                output = f"{Url} {StatusCode}{Jarm}{Title}{Server}{Apt}{Wc}{Lc}{Lt}{Lo}{A}{Cn}{AAA}{Htv}{Htr}{Rpt}{Wss}{Hsh}{Dmt}{Bpv}"
                stdinlog(output)
                if self.args.output:
                    await save(self.args.output, output, self.args.json, self.args.no_color)
                    
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger("CTRL+C Pressed!", "debug", self.args.no_color)
            exit(1)
        except Exception as e:
            logger(f"Exception occured in subprober core manager module due to: {e}, {type(e)}", "warn", self.args.no_color)
        finally:
            bar()
    
    async def start(self) -> None:
        try:
            
            if self.args.screenshot:
                self.screenshots = Headless(self.args)
                self.screenshots.setup()
            
            if self.args.retries:
                transport = AsyncHTTPTransport(retries=self.args.retries)
            else:
                transport = None
                
            timeout = httpx.Timeout(connect=self.args.timeout, pool=self.args.concurrency*2, write=None, read=80.0)
            limits = httpx.Limits(max_connections=self.args.concurrency*2, max_keepalive_connections=self.args.concurrency*2)
            
            async with httpx.AsyncClient(verify=False, limits=limits, http2=self.args.http2, max_redirects=self.args.max_redirection, proxy=self.args.proxy, transport=transport, timeout=timeout)   as session:
                with alive_bar(title="SubProber", total=len(self.urls), enrich_print=False) as bar:
                    for chunk in chunker(self.urls):
                        tasks = []
                        for url in chunk:
                            await self.semaphore.acquire()
                            task = asyncio.create_task(self.manage(url, self.args.method,bar,session))
                            tasks.append(task)
                        await asyncio.gather(*tasks, return_exceptions=True)
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger("CTRL+C Pressed!", "debug", self.args.no_color)
            exit(1)
        except Exception as e:
            if self.args.verbose:
                logger(f"Exception occured in the subprober start module due to: {e}, {type(e)}", "warn", self.args.no_color)