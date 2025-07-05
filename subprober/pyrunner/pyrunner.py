import argparse
import asyncio
import httpx
import sys
import os
import aiofiles
from alive_progress import alive_bar
from aiolimiter import AsyncLimiter
import signal
from subprober.responser.responser import Responser
from subprober.tempdirs.tempdirs import AsyncTempdir
from subprober.tempfiles.tempfiles import AsyncTempfile
from subprober.logger.logger import Logger
from subprober.utils.utils import Utils
from subprober.httpz import httpz
from subprober.cache.cache import AsyncDiskCache
from subprober.screenshot.screenshot import Headless
from subprober.progressbar.progressbar import ProgressBar


class Runner:
    def __init__(self, args: argparse.Namespace) -> None:
        self.logger = Logger()
        self.tmpdir = AsyncTempdir()
        self.tmpfile = AsyncTempfile()
        self.probe_bar = None
        self.db_bar = None
        self.resume_bar = None
        self.args = args
        self.tmpdirpath = None
        self.tmpfilepath = None
        self.diskcache = None
        self.semaphore = asyncio.Semaphore(self.args.concurrency)
        self.totalprocess = 0
        self.httptimeout = None
        self.limits = httpx.Limits(max_connections=self.args.concurrency * 2,
                                   max_keepalive_connections=self.args.concurrency * 2)
        self.timeout = httpx.Timeout(connect=self.args.timeout, pool=None, write=None, read=80.0)
        self.utils = Utils()
        self.inputer = None
        self.resparser = None
        self.nameservers = ["8.8.8.8", "1.1.1.1"]
        self.paths = None
        self.ports = None
        self.request_headers = {}
        self.requester = httpz.AsyncClientz(
            disable_http_fallback=self.args.disable_http_probe,
            retries=self.args.retries,
            proxy=self.args.proxy,
            timeout=self.timeout,
            limits=self.limits,
            http2=self.args.http2,
            max_redirects=self.args.max_redirection,
            verify=False
        )
        self.rate_limit = AsyncLimiter(self.args.rate_limit, 1)
        self.stop_requested = False
        self._lock = asyncio.Lock()
        self.screenshoter = Headless(self.args)
        self.db_adder_sem = asyncio.Semaphore(200)
        self.probe_started = False
        self._pychannel = asyncio.Queue(maxsize=self.args.concurrency * 2)
        self._dbchannel = asyncio.Queue(maxsize=10000)
        self._event = asyncio.Event()
        self._dbevent = asyncio.Event()

    async def setup(self):
        try:
            self.tmpdirpath = await self.tmpdir.create()
            self.diskcache = AsyncDiskCache(self.tmpdirpath)
            if self.args.screenshot:
                await self.screenshoter.init_browser()
            await self.requester.init()
            if self.args.output:
                await self.utils.permissions(self.args.output)

            if self.args.resolvers:
                self.nameservers = self.utils.string_to_str_list(self.args.resolvers)

            if self.args.port:
                self.ports = self.utils.string_to_int_list(self.args.port)

            if self.args.path:
                self.paths = await self.utils.Reader(self.args.path, self.args) if os.path.isfile(
                    self.args.path) else self.utils.string_to_str_list(self.args.path)

            if self.args.header:
                for header_str in self.args.header:
                    try:
                        name, value = header_str.split(':', 1)
                        self.request_headers[name.strip()] = value.strip()
                    except ValueError:
                        self.logger.warn(f"Invalid header format: '{header_str}'. Expected 'Name:Value'.")

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
                    await self.tmpfile.write(url+"\n")
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
                    await self.tmpfile.write(url + "\n")
                return
        except Exception as e:
            self.logger.warn(f"Error occured in the inputsetter method of runner pkg due to: {e}")

    async def _add_to_cache(self, url: str) -> None:
        async with self.db_adder_sem:
            urls_to_process = self.utils.validate_and_expand_urls(
                url, ports=self.ports, paths=self.paths
            )
            for final_url in urls_to_process:
                final_url = final_url.strip()
                if await self.diskcache.add(final_url,True):
                    self.totalprocess += 1
                    self.db_bar()

    async def dbproducer(self) -> None:
        try:

            async def producer():
                async with aiofiles.open(self.inputer, "r") as streamr:
                    async for line in streamr:
                        url = line.strip()
                        if not url:
                            continue
                        await self._dbchannel.put(url)
                    self._dbevent.set()
            async def processor(url: str):
                try:
                    await self._add_to_cache(url)
                finally:
                    self._dbchannel.task_done()

            async def consumer():
                while True:
                    url = await self._dbchannel.get()
                    asyncio.create_task(processor(url))

            #db progress is different from other states so we use alive_bar
            with alive_bar(None, title="Loading... URLs (unique)", enrich_print=False) as self.db_bar:
                self._dbevent.clear()
                dbtasks = []
                dbtasks.append(
                    asyncio.create_task(producer())
                )
                for _ in range(500):
                    dbtasks.append(
                        asyncio.create_task(consumer())
                    )

                await self._dbevent.wait()
                await self._dbchannel.join()
                for task in dbtasks:
                    task.cancel()
        except Exception as e:
            self.logger.warn(f"Error in dbproducer: {e}")


    async def cleanup(self) -> None:
        try:
            if self.args.screenshot:
                await self.screenshoter.close_browser()
            if self.requester is not None:
                await self.requester.close()
            if self.tmpdirpath and os.path.exists(self.tmpdirpath):
                await self.tmpdir.close()
            if self.tmpfilepath and os.path.exists(self.tmpfilepath):
                await self.tmpfile.close()
        except RuntimeError:
            pass
        except Exception :
            pass

    async def probe(self, method: str, url: str, redirect=True):
        try:
            async with self.rate_limit:
                self.request_headers["User-Agent"] = self.utils.Useragents() if self.args.random_agent else "git+Subprober/V2"
                extensions = None
                if self.args.sni_hostname:
                    extensions = {"sni_hostname": self.args.sni_hostname}
                responses = await self.requester.request(
                    method,
                    url,
                    content=self.args.body,
                    headers=self.request_headers,
                    follow_redirects=redirect,
                    extensions=extensions)
                for url, response in responses.items():
                    if response is None:
                        continue
                    results = await self.resparser.responseparser(response, url)
                    if results:
                        if self.args.screenshot:
                            async with self.semaphore: # 1 entry 2 response so using semaphore to block it based on concurrency
                                await self.screenshoter.run(url, results)
                        await self.resparser.resultsparser(results=results, url=url)
        except httpx.TooManyRedirects:
            await self.probe(method, url, False)
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Error occurred during probing to the url {url} due to: {e}")

    async def _safe_probe_(self, method: str, url: str, redirect=True):
            try:
                await self.probe(method, url, redirect)
            except Exception as e:
                self.logger.warn(f"Error occurred in safe probing method for url {url} and due to: {e}")
            finally:
                if not self.stop_requested:
                    self.probe_bar.update()
                    await self.diskcache.delete(url)

    async def producer(self) -> None:
        async for url in self.diskcache.iterkeys():
            await self._pychannel.put(url)
        self._event.set()

    async def consumer(self) -> None:
        while not self.stop_requested:
            url = await self._pychannel.get()
            await self._safe_probe_(self.args.method.upper(), url, self.args.allow_redirect)
            self._pychannel.task_done()

    async def sprint(self):
        try:
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGINT, self._signal_handler)
            await self.setup()
            await self.setinput()
            await self.dbproducer()

            if self.totalprocess == 0:
                self.logger.info("No URLs to process. Exiting.")
                await self.cleanup()
                exit(0)
            self.probe_started = True

            self.probe_bar = ProgressBar(total=self.totalprocess, title="Subprober")
            self.probe_bar.start()
            tasks = []
            self._event.clear()
            tasks.append(
                asyncio.create_task(self.producer())
            )

            for _ in range(self.args.concurrency):
                tasks.append(
                    asyncio.create_task(self.consumer())
                )

            await self._event.wait()
            await self._pychannel.join()
            for task in tasks:
                task.cancel()
            self.probe_bar.close()
        except Exception as e:
            self.logger.error(f"Error occurred in the main sprint method: {e}")
        finally:
            await self.cleanup()

    async def save_resume_file(self):
        self.probe_bar.close() # close the previous progress context to start for new for resume state saving!
        filename = f"resume_{self.utils.generate_random()}.cfg"
        disklen = await self.diskcache.size()
        self.resume_bar = ProgressBar(total=disklen, title="Saving Resume...")
        self.resume_bar.start()
        async with aiofiles.open(filename, "w") as streamw:
            async for url in self.diskcache.iterkeys():
                await streamw.write(url + "\n")
                self.resume_bar.update()
        self.resume_bar.close()
        self.logger.info(f"saved the resume file successfully: {filename}")

    def _signal_handler(self):
        self.logger.warn("CTRL+C pressed!.Saving resume file please wait")
        self.stop_requested = True
        asyncio.create_task(self._handle_interrupt())

    async def _handle_interrupt(self):
        if self.probe_started:
            await self.save_resume_file()
        await self.cleanup()
        await asyncio.sleep(5)
        os._exit(1)
