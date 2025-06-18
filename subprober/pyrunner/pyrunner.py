from subprober.requester.requester import Requester
from subprober.responser.responser import Responser
from diskcache import Cache
from subprober.tempdirs.tempdirs import AsyncTempdir
from subprober.tempfiles.tempfiles import AsyncTempfile
from subprober.logger.logger import Logger
from subprober.utils.utils import Utils
import argparse
import asyncio
from asyncio import Queue
import httpx
from httpx import AsyncHTTPTransport
import sys
import os
import aiofiles
from alive_progress import alive_bar
from asynciolimiter import Limiter
import signal

class Runner():
    def __init__(self, args: argparse.Namespace):
        self.logger = Logger()
        self.tmpdir = AsyncTempdir()
        self.tmpfile = AsyncTempfile()
        self.bar = None
        self.args = args
        self.tmpdirpath = None
        self.tmpfilepath = None
        self.streamqueue = Queue(maxsize=0)
        self.diskcache = None
        self.semaphore = asyncio.Semaphore(self.args.concurrency)
        self.totalprocess = 0
        self.httptransport = None
        self.httptimeout = None
        self.limits = None
        self.utils = Utils()
        self.inputer = None
        self.resparser = None
        self.nameservers = ["8.8.8.8", "1.1.1.1"]
        self.paths = None
        self.requester = Requester(self.args)
        self.rate_limit = Limiter(rate=self.args.rate_limit/1)
        self.stop_requested = False
        self._lock = asyncio.Lock()
        
    async def setup(self):
        try:                
            if self.args.retries:
                self.httptransport = AsyncHTTPTransport(retries=self.args.retries)
                
            self.timeout = httpx.Timeout(connect=self.args.timeout, pool=None, write=None, read=80.0)
            self.limits = httpx.Limits(max_connections=self.args.concurrency*2, max_keepalive_connections=self.args.concurrency*2)
            self.tmpdirpath = await self.tmpdir.create()
            self.diskcache = Cache(self.tmpdirpath)
            
            if self.args.output:
                await self.utils.permissions(self.args.output)
                
            if self.args.resolvers:
                self.nameservers = self.utils.string_to_str_list(self.args.resolvers)
                
            if self.args.path:
                self.paths = await self.utils.Reader(self.args.path,self.args) if os.path.isfile(self.args.path) else self.utils.string_to_str_list(self.args.path)
                
            self.resparser = Responser(
                self.args, 
                nameservers=self.nameservers,
                hashes=self.utils.string_to_str_list(self.args.hash), 
                mc=self.utils.string_to_int_list(self.args.match_code),
                fc=self.utils.string_to_int_list(self.args.filter_code),
                mcr=self.args.match_code_range,
                fcr=self.args.filter_code_range,
                ms=self.utils.string_to_str_list(self.args.match_string),
                fs=self.utils.string_to_str_list(self.args.filter_string),
                mrg=self.utils.string_to_str_list(self.args.match_regex),
                frg=self.utils.string_to_str_list(self.args.filter_regex),
                mpt=self.utils.string_to_str_list(self.args.match_path),
                fpt=self.utils.string_to_str_list(self.args.filter_path),
                ml=self.utils.string_to_int_list(self.args.match_length),
                fl=self.utils.string_to_int_list(self.args.filter_length),
                mlc=self.utils.string_to_int_list(self.args.match_line_count),
                flc=self.utils.string_to_int_list(self.args.filter_line_count), 
                mwc=self.utils.string_to_int_list(self.args.match_word_count),
                fwc=self.utils.string_to_int_list(self.args.filter_word_count),
                mrt=self.args.match_response_time, 
                frt=self.args.filter_response_time 
                )
        except Exception as e:
            self.logger.warn(f"Error occured in the setup method of runner pkg due to: {e}")
            
    async def setinput(self):
        try:
            if self.args.url:
                urls = self.utils.string_to_str_list(self.args.url)
                self.tmpfilepath = await self.tmpfile.create()
                self.inputer = self.tmpfilepath
                for url in urls:
                    await self.tmpfile.write(url)
                return
            
            if self.args.filename:
                if not os.path.exists(self.args.filename):
                    self.logger.warn(f"{self.args.filename} no such file or directory exist")
                    await self.cleanup()
                    exit(1)
                else:
                    self.inputer = self.args.filename
                return
            
            if self.args.resume:
                if not os.path.exists(self.args.resume):
                    self.logger.warn(f"{self.args.resume} no such file or directory exist")
                    await self.cleanup()
                    exit(1)
                else:
                    self.inputer = self.args.resume
                return
            
            if sys.stdin.isatty():
                self.logger.warn(f"no inputs provided for subprober")
                await self.cleanup()
                exit(1)
            else:
                urls = [domain.strip() for domain in sys.stdin if domain.strip()]
                self.tmpfilepath = await self.tmpfile.create()
                self.inputer = self.tmpfilepath
                for url in urls:
                    await self.tmpfile.write(url+"\n")
                return
        except Exception as e:
            self.logger.warn(f"Error occured in the inputsetter method of runner pkg due to: {e}")
            
    async def dbproducer(self) -> None:
        try:
            async with aiofiles.open(self.inputer, "r") as streamr:
                async for url_line in streamr:
                    urls_to_process = self.utils.validate_url(url_line.strip(),self.args.disable_http_probe)
                    
                    if self.args.port:
                        ports = self.utils.string_to_int_list(self.args.port)
                        urls_to_process = self.utils.add_ports_to_urls(urls_to_process, ports=ports)
                    
                    if self.paths: 
                        urls_to_process = self.utils.add_paths_to_urls(urls_to_process, self.paths)
                    
                    for final_url in urls_to_process:
                        final_url = final_url.strip()
                        if final_url: 
                            if final_url not in self.diskcache:
                                self.diskcache[final_url] = True 
                                async with self._lock:
                                    self.totalprocess += 1
        except FileNotFoundError:
            self.logger.warn(f"Error occured finding the input , please try again")
            raise
        except Exception as e:
            self.logger.warn(f"Error occured in the db producer method due to: {e}")
            
            
    async def cleanup(self) -> None:
        if self.tmpdirpath and os.path.exists(self.tmpdirpath):
            await self.tmpdir.close()
        if self.tmpfilepath and os.path.exists(self.tmpfilepath):
            await self.tmpfile.close()
            
    async def dbstreamer(self) -> None:

        try:
            for url in self.diskcache.iterkeys():
                await self.streamqueue.put(url)
            for _ in range(self.args.concurrency):
                await self.streamqueue.put(None)
        except Exception as e:
            self.logger.warn(f"Error occured in the db streamer method due to: {e}")
            raise
            
    async def probe(self, method, url, client):
        response = await self.requester.request(method, url, client, content=self.args.body)
        if response is None:
            return                     
        results = await self.resparser.responseparser(response, url) 
        if results is None:
            return
        await self.resparser.resultsparser(results=results, url=url)
            
    async def dbconsumer(self, client:httpx.AsyncClient, method:str) -> None:
        while not self.stop_requested:
            url = await self.streamqueue.get()
            if url is None:
                self.streamqueue.task_done()
                break 
            try:
                await self.rate_limit.wait()
                await self.probe(method, url, client)
            except Exception as e:
                self.logger.warn(f"Error occured in the db consumer method due to: {e}")
            finally:
                self.streamqueue.task_done() 
                if not self.stop_requested: # prevents inaccuracies in saving the state!
                    self.diskcache.delete(url)
                    self.bar()
    
    async def sprint(self):
        try:
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGINT, self._signal_handler)
            await self.setup()
            await self.setinput()
            await self.dbproducer()
            await self.dbstreamer()
            async with httpx.AsyncClient(verify=False, transport=self.httptransport, timeout=self.timeout, limits=self.limits, http2=self.args.http2, max_redirects=self.args.max_redirection, proxy=self.args.proxy) as client:
                with alive_bar(title="SubProber", total=self.totalprocess, enrich_print=False) as bar:
                    self.bar = bar
                    tasks = [asyncio.create_task(self.dbconsumer(client, self.args.method))  
                             for _ in range(self.args.concurrency)] # Like goroutines in golang we spawn coroutines for python!
                    await self.streamqueue.join()
                    await asyncio.gather(*tasks, return_exceptions=True) 
        except Exception as e:
            self.logger.error(f"Error occurred in the main sprint method: {e}")
        finally:
            await self.cleanup()
            exit(0)
            
    def save_resume_file(self):
        filename = f"resume_{self.utils.generate_random()}.cfg"
        with open(filename, "w") as streamw:
            for url in self.diskcache.iterkeys():
                streamw.write(url + "\n")
        self.logger.info(f"saved the resume file successfully: {filename}")
            
    def _signal_handler(self):
        self.logger.warn("CTRL+C pressed!.Saving resume file please wait")
        self.stop_requested = True
        self.save_resume_file()
        asyncio.create_task(self.cleanup())
        asyncio.create_task(self._exit_after_cleanup())
        
    async def _exit_after_cleanup(self):
        await asyncio.sleep(0.1)  
        await self.cleanup()
        os._exit(1)