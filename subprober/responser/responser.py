import httpx
import warnings
import argparse
from datetime import datetime
from bs4 import  XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning, BeautifulSoup, FeatureNotFound
import json
from subprober.utils.utils import Utils
from subprober.logger.logger import Logger
from subprober.matchers.matchers import *
from subprober.filters.filters import *
from subprober.hash.hash import HashGen
from subprober.jarmhash.jarmhash import JarmScanner
from subprober.dns.dns import AsyncDns
from subprober.tls.tls import TlsCert
from subprober.asyncwebsocket.asyncwebsocket import AsyncWebsocket
from subprober.save.save import Save

class Responser:
    def __init__(
        self,
        args: argparse.Namespace,
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
        fl = None) -> None:
        
        self.args = args
        self.nameservers = nameservers
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
        self.logger = Logger()      
        self.reset = self.logger.reset
        self.white = self.logger.white
        self.bold = self.logger.bold
        self.green = self.logger.green
        self.yellow = self.logger.yellow
        self.red = self.logger.red
        self.magenta = self.logger.magenta
        self.cyan = self.logger.cyan
        self.blue = self.logger.blue  
        self.random_color = self.logger.random_color
        self.utils = Utils()
        self.hasher = HashGen(self.hashes, self.args)
        self.jarmscanner = JarmScanner(self.args)
        self.dnsresolver = AsyncDns(self.args, self.nameservers)
        self.tlsscanner = TlsCert()
        self.websocketer = AsyncWebsocket(self.args)
        self.saver = Save(filename=self.args.output, jsonize=self.args.json)
        
    async def responseparser(self, response:httpx.Response, url: str) -> dict:
        try:
            results = {}
            network_streams = response.extensions.get("network_stream")
            server_addr = network_streams.get_extra_info("server_addr") if network_streams else None
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
                
            results["Cookies"] = self.utils.extract_cookies(response.cookies.jar) if response.cookies.jar else []
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
                    self.logger.warn(f"Looks like your beautifulsoup4, lxml, bs4 not in latest version, please update it")
                results["Title"] = ""
            
            if self.args.hash:
                hashes= await self.hasher.gen(str(response.text))
                results["Hash"] = hashes if hashes else {}
            
            if self.args.jarm_fingerprint:
                jarmhashes = await self.jarmscanner.get_jarm_hash(url)
                results["JarmHash"] = jarmhashes
            
            if self.args.full_output or self.args.cname:
                cname = await self.dnsresolver.resolve(url, "CNAME")
                results["Cname"] = cname

            if self.args.full_output or self.args.ipaddress:
                ips = await self.dnsresolver.resolve(url, "A")
                results["A"] = ips

            if self.args.full_output or self.args.aaa_records:
                aaaa = await self.dnsresolver.resolve(url, "AAAA")
                results["AAAA"] = aaaa
                
            results["Server"] = response.headers.get("server", "")
            
            content_type = response.headers.get("Content-Type", "")
            if content_type:
                content_type = content_type.split(";")[0].strip()
                results["ContentType"] = content_type
            else:
                results["ContentType"] = ""
                
            if self.args.websocket:
                websocket = await self.websocketer.asyncconnect(url)
                results["Websockets"] = websocket
            
            if self.args.full_output or self.args.tls and self.args.json:
                tls = await self.tlsscanner.tlsinfo(network_streams)
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
                    return results
            else:
                results =  None
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occured in the response handler module due to: {e}, {type(e)}, {url}")
                
    
    async def resultsparser(self, results: dict, url: str):
        try:
            if results is None:
                return 
    
            if self.args.json:
                self.logger.stdin(json.dumps(results, ensure_ascii=False))
                if self.args.output:
                    await self.saver.save(results)
                return

            if not self.args.no_color:
                Url = f"{self.bold}{self.white}{results['Url']}"
                
                sc = results["StatusCode"]
                if self.args.status_code:
                    if sc >= 200 and sc <= 299:
                        StatusCode = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.green}{sc}{self.reset}{self.bold}{self.white}]{self.reset}"
                    elif sc >= 300 and sc <= 399:
                        StatusCode = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.yellow}{sc}{self.reset}{self.bold}{self.white}]{self.reset}"
                    else:
                        StatusCode = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.red}{sc}{self.reset}{self.bold}{self.white}]{self.reset}"
                else:
                    StatusCode = ""
                
                Jarm = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.magenta}{results.get('JarmHash', {}).get('hash', 'N/A')}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.jarm_fingerprint and results.get('JarmHash') else ""
                Title = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.cyan}{results['Title']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.title else ""
                Server = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.magenta}{results['Server']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.server else ""
                Wc = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.green}{results['WordCount']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.word_count else ""
                Lc = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.red}{results['LineCount']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.line_count else ""
                Lt = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.green}{results['Length']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.content_length else ""
                Lo = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.magenta}{results['FinalUrl']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.location and self.args.allow_redirect else ""
                Apt = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.yellow}{results['ContentType']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.application_type else ""
                A = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.yellow}{','.join(map(str, results.get('A', [])))}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.ipaddress and results.get('A') else ""
                Cn = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.green}{','.join(map(str, results.get('Cname', [])))}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.cname and results.get('Cname') else ""
                AAA = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.cyan}{','.join(map(str, results.get('AAAA', [])))}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.aaa_records and results.get('AAAA') else ""
                Htv = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.blue}{results['HttpVersion']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.http_version else ""
                Htr = f"{self.bold}{self.white}[{self.reset}{self.bold}{self.magenta}{results['ResponseReason']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.http_reason else ""
                Rpt = f"{self.bold}{self.white}[{self.reset}{self.random_color}{results['ResponseTime']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.response_time else ""
                Wss = f"{self.bold}{self.white}[{self.reset}{self.random_color}websocket: {results.get('Websockets', 'N/A')}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.websocket else ""
                Hsh_values = results.get('Hash', {}).values()
                Hsh = f"{self.bold}{self.white}[{self.reset}{self.random_color}{','.join(map(str, Hsh_values))}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.hash and Hsh_values else ""
                Dmt = f"{self.bold}{self.white}[{self.reset}{self.random_color}{results['Method']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.display_method else ""
                Bpv = f"{self.bold}{self.white}[{self.reset}{self.random_color}{results['BodyPreview']}{self.reset}{self.bold}{self.white}]{self.reset}" if self.args.body_preview else ""
            else:
                Url = f"{results['Url']}"
                StatusCode = f"[{results['StatusCode']}]" if self.args.status_code else ""
                Jarm = f"[{results.get('JarmHash', {}).get('hash', 'N/A')}]" if self.args.jarm_fingerprint and results.get('JarmHash') else ""
                Title = f"[{results['Title']}]" if self.args.title else ""
                Server = f"[{results['Server']}]" if self.args.server else ""
                
                Wc = f"[{results['WordCount']}]" if self.args.word_count else ""
                Lc = f"[{results['LineCount']}]" if self.args.line_count else ""
                Lt = f"[{results['Length']}]" if self.args.content_length else ""
                Lo = f"[{results['FinalUrl']}]" if self.args.location and self.args.allow_redirect else ""
                Apt = f"[{results['ContentType']}]" if self.args.application_type else ""
                A = f"[{','.join(map(str, results.get('A', [])))}]" if self.args.ipaddress and results.get('A') else ""
                Cn = f"[{','.join(map(str, results.get('Cname', [])))}]" if self.args.cname and results.get('Cname') else ""
                AAA = f"[{','.join(map(str, results.get('AAAA', [])))}]" if self.args.aaa_records and results.get('AAAA') else ""

                Htv = f"[{results['HttpVersion']}]" if self.args.http_version else ""
                Htr = f"[{results['ResponseReason']}]" if self.args.http_reason else ""
                Rpt = f"[{results['ResponseTime']}]" if self.args.response_time else ""
                Wss = f"[websocket: {results.get('Websockets', 'N/A')}]" if self.args.websocket else ""
                Hsh_values = results.get('Hash', {}).values()
                Hsh = f"[{','.join(map(str, Hsh_values))}]" if self.args.hash and Hsh_values else ""
                
                Dmt = f"[{results['Method']}]" if self.args.display_method else ""
                Bpv = f"[{results['BodyPreview']}]" if self.args.body_preview else ""

            output = f"{Url} {StatusCode}{Jarm}{Title}{Server}{Apt}{Wc}{Lc}{Lt}{Lo}{A}{Cn}{AAA}{Htv}{Htr}{Rpt}{Wss}{Hsh}{Dmt}{Bpv}"
            self.logger.stdin(output)
            if self.args.output:
                await self.saver.save(output)
            return
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occurred in Responser.resultsparser for URL: '{url}' due to: {e}, {type(e)}")
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occured in the results parser module due to: {e}, {type(e)}, {url}")