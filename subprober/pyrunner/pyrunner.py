import asyncio
import aiohttp
from revoltutils import (FileUtils, AsyncTempdir, AsyncTempfile,
                         AsyncQueue, ProgressBar, GenericUtils, PermissionUtils,
                         IPUtils, HttpUtils, RandomUtils)
from revoltlogger import Logger, LogLevel
from subprober.settings.settings import Settings
from subprober.resparser.resparser import Resparser
from subprober.headless.headless import Headless
from subprober.httpfilters.httpfilters import HttpFilter, HttpMatcher
from subprober.httpclient.httpclient import RetryableHttp, BackoffStrategy
from subprober.utils.utils import Utils, InputValidator
from subprober.urlbuilder.urlbuilder import URLBuilder
from subprober.progresslogger.progresslogger import ProgressLogger
from subprober.hmap.hmap import HMap
from subprober.workerpool.workerpool import WorkerPool
from khonshu.cidr.cidr import NETStreamer
from typing import Optional, List, Dict, Any, AsyncGenerator
from aiolimiter import AsyncLimiter
import os
import sys
import signal
import ssl

class PyRunner:
    def __init__(self, settings: Settings) -> None:
        self.args = settings
        self.logger = Logger(level=LogLevel.DEBUG, colored=not self.args.no_color)

        # Temp directories
        self.tempdir = AsyncTempdir()
        self.tempresume = AsyncTempdir()
        self.tempfile = AsyncTempfile()
        self.tmpdirpath = None
        self.tmpfilepath = None
        self.tmpresumepath = None
        self.inputer = None

        # LevelDB-based disk cache for host deduplication
        self.hmap: Optional[HMap] = None
        self._resume_marker: Optional[Dict[str, Any]] = None

        # NO separate path/port caches - stream directly from files!
        self._path_file: Optional[str] = None
        self._port_file: Optional[str] = None
        self._paths_list: List[str] = []  # Only for small lists (<100)
        self._ports_list: List[int] = []  # Only for small lists (<100)

        # Worker pool (replaces WaitGroups semaphore)
        self.pool: Optional[WorkerPool] = None

        # Utils
        self.utils = Utils()
        self.generic = GenericUtils()
        self.fileutils = FileUtils()
        self.validator = InputValidator()
        self.cidr_streamer = NETStreamer(max_size=2000)
        self._url_builder = URLBuilder()
        self.ip_utils = IPUtils()
        self.httputils = HttpUtils()
        self.randomutils = RandomUtils()

        self.task_started = False

        # Configs
        self.nameserver = ["8.8.8.8", "1.1.1.1"]
        self.request_headers: Dict[str, str] = {}

        # HTTP client
        self.connector = None
        self.timeout_config = None
        self.requester = None

        # Rate limiter
        self.rate_limit = AsyncLimiter(self.args.rate_limit, 1.0)

        # Flags
        self.stop = False

        # Components
        self.headlessclient: Optional[Headless] = None
        self.resparser: Optional[Resparser] = None

        # Counters
        self.db_total = 0
        self.progress_total = 0
        self.port_total = 0
        self.path_total = 0
        self._completed_tasks = 0
        self._failed_tasks = 0

        # Progress tracking
        self.cache_bar: Optional[ProgressBar] = None
        self.probe_bar: Optional[ProgressBar] = None
        self.resume_bar: Optional[ProgressBar] = None
        self.cache_logger: Optional[ProgressLogger] = None
        self.probe_logger: Optional[ProgressLogger] = None
        self.resume_logger: Optional[ProgressLogger] = None

        # Events
        self._shutdown = asyncio.Event()

        # Per-host completion tracking (bounded by in-flight hosts only, ~concurrency * 3)
        self._host_pending: dict[str, int] = {}    # host → count of unfinished URLs
        self._host_all_submitted: set[str] = set() # hosts where producer finished expanding

        # output channels — sized to concurrency to avoid backpressure from output
        self._output_chan = AsyncQueue(maxsize=max(100, self.args.concurrency))

        # Filters
        self.matcher = HttpMatcher()
        self.filter = HttpFilter()
        self._parse_match_filter_args()

    def _parse_match_filter_args(self) -> None:
        """Parse match/filter arguments"""
        self.mc = self._parse_int_list(self.args.match_code) if hasattr(self.args, 'match_code') else None
        self.mcr = self.args.match_code_range if hasattr(self.args, 'match_code_range') else None
        self.ms = self._parse_string_list(self.args.match_string) if hasattr(self.args, 'match_string') else None
        self.mrg = self._parse_string_list(self.args.match_regex) if hasattr(self.args, 'match_regex') else None
        self.mpt = self._parse_string_list(self.args.match_path) if hasattr(self.args, 'match_path') else None
        self.ml = self._parse_int_list(self.args.match_length) if hasattr(self.args, 'match_length') else None
        self.mlc = self._parse_int_list(self.args.match_line_count) if hasattr(self.args, 'match_line_count') else None
        self.mwc = self._parse_int_list(self.args.match_word_count) if hasattr(self.args, 'match_word_count') else None
        self.mrt = self.args.match_response_time if hasattr(self.args, 'match_response_time') else None

        self.fc = self._parse_int_list(self.args.filter_code) if hasattr(self.args, 'filter_code') else None
        self.fcr = self.args.filter_code_range if hasattr(self.args, 'filter_code_range') else None
        self.fs = self._parse_string_list(self.args.filter_string) if hasattr(self.args, 'filter_string') else None
        self.frg = self._parse_string_list(self.args.filter_regex) if hasattr(self.args, 'filter_regex') else None
        self.fpt = self._parse_string_list(self.args.filter_path) if hasattr(self.args, 'filter_path') else None
        self.fl = self._parse_int_list(self.args.filter_length) if hasattr(self.args, 'filter_length') else None
        self.flc = self._parse_int_list(self.args.filter_line_count) if hasattr(self.args,
                                                                                'filter_line_count') else None
        self.fwc = self._parse_int_list(self.args.filter_word_count) if hasattr(self.args,
                                                                                'filter_word_count') else None
        self.frt = self.args.filter_response_time if hasattr(self.args, 'filter_response_time') else None

    def _parse_int_list(self, value: Any) -> Optional[List[int]]:
        if not value:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return self.generic.string_to_int_list(value, ",")
        return None

    def _parse_string_list(self, value: Any) -> Optional[List[str]]:
        if not value:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return self.generic.string_to_string_list(value, ",")
        return None

    async def _apply_match_filter_conditions(
            self,
            response: Any,
            text: str,
            **kwargs
    ) -> bool:
        """Apply match/filter conditions"""
        status_code = response.status_code if hasattr(response, 'status_code') else response.status
        content_length = len(text)
        line_count = text.count('\n') + 1 if text else 0
        word_count = len(text.split()) if text else 0

        # Match conditions
        if self.mc and not await self.matcher.match_by_code(response, self.mc, **kwargs):
            return False
        if self.mcr and not await self.matcher.match_code_range(response, self.mcr, **kwargs):
            return False
        if self.mpt and not await self.matcher.match_url_path_contains(response, self.mpt, **kwargs):
            return False
        if self.ms and not await self.matcher.match_word_body(response, self.ms, **kwargs):
            return False
        if self.mrg and not await self.matcher.match_by_regex(response, self.mrg, **kwargs):
            return False
        if self.mrt and not await self.matcher.match_response_time(response, self.mrt, **kwargs):
            return False
        if self.ml and not await self.matcher.match_by_ints(content_length, self.ml):
            return False
        if self.mlc and not await self.matcher.match_by_ints(line_count, self.mlc):
            return False
        if self.mwc and not await self.matcher.match_by_ints(word_count, self.mwc):
            return False

        # Filter conditions
        if self.fc and not await self.filter.filter_by_code(response, self.fc, **kwargs):
            return False
        if self.fcr and not await self.filter.filter_code_range(response, self.fcr, **kwargs):
            return False
        if self.fpt and not await self.filter.filter_url_path_contains(response, self.fpt, **kwargs):
            return False
        if self.fs and not await self.filter.filter_word_body(response, self.fs, **kwargs):
            return False
        if self.frg and not await self.filter.filter_by_regex(response, self.frg, **kwargs):
            return False
        if self.frt and not await self.filter.filter_response_time(response, self.frt, **kwargs):
            return False
        if self.fl and not await self.filter.filter_by_ints(content_length, self.fl):
            return False
        if self.flc and not await self.filter.filter_by_ints(line_count, self.flc):
            return False
        if self.fwc and not await self.filter.filter_by_ints(word_count, self.fwc):
            return False

        return True

    async def setup(self) -> None:
        """Setup the pyrunner"""
        try:
            if self.args.debug:
                self.logger.debug("Starting setup...")

            if self.args.output:
                if not PermissionUtils.is_writable(self.args.output):
                    self.logger.error(f"No permission: {self.args.output}")
                    exit(1)

            # Create temp directory
            self.tmpdirpath = await self.tempdir.create()

            # LevelDB disk cache for host deduplication
            if self._resume_marker:
                # Resume: open existing persisted LevelDB
                hmap_path = self._resume_marker["hmap_path"]
                if not os.path.exists(hmap_path):
                    self.logger.error(f"Resume HMap not found: {hmap_path}")
                    self.logger.error("The LevelDB directory may have been deleted. Cannot resume.")
                    exit(1)
                self.hmap = HMap(
                    path=hmap_path,
                    write_buffer_size=4 * 1024 * 1024,
                    lru_cache_size=8 * 1024 * 1024,
                    bloom_filter_bits=10,
                    batch_size=1000,
                )
            else:
                # Normal: create new temp HMap
                self.hmap = HMap(
                    write_buffer_size=4 * 1024 * 1024,
                    lru_cache_size=8 * 1024 * 1024,
                    bloom_filter_bits=10,
                    batch_size=1000,
                )

            if self.args.path:
                if await self.fileutils.file_exist(self.args.path):
                    self._path_file = self.args.path
                    # Count without loading
                    async for _ in self.fileutils.stream(self.args.path):
                        self.path_total += 1

                    if self.args.debug:
                        self.logger.debug(f"Path file: {self._path_file} ({self.path_total:,} paths)")
                else:
                    self._paths_list = self.generic.string_to_string_list(self.args.path, ",")
                    self.path_total = len(self._paths_list)

                    if self.args.debug:
                        self.logger.debug(f"Paths in memory: {self.path_total}")

            if self.args.port:
                if await self.fileutils.file_exist(self.args.port):
                    self._port_file = self.args.port
                    async for _ in self.fileutils.stream(self.args.port):
                        self.port_total += 1

                    if self.args.debug:
                        self.logger.debug(f"Port file: {self._port_file} ({self.port_total} ports)")
                else:
                    self._ports_list = self.generic.string_to_int_list(self.args.port, ",")
                    self.port_total = len(self._ports_list)

                    if self.args.debug:
                        self.logger.debug(f"Ports in memory: {self.port_total}")

            self.tmpresumepath = await self.tempresume.create()

            # Resolvers
            if self.args.resolvers:
                if await self.fileutils.file_exist(self.args.resolvers):
                    self.nameserver = await self.fileutils.readlines(self.args.resolvers)
                else:
                    self.nameserver = self.generic.string_to_string_list(self.args.resolvers, ",")

            # HTTP client
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            self.connector = aiohttp.TCPConnector(
                limit=self.args.concurrency,
                limit_per_host=min(10, self.args.concurrency),
                ssl=ssl_context,
                force_close=False,
                enable_cleanup_closed=True,
                ttl_dns_cache=300
            )

            self.timeout_config = aiohttp.ClientTimeout(
                total=None,
                connect=self.args.timeout,
                sock_read=80.0
            )

            self.requester = RetryableHttp(
                connector=self.connector,
                timeout=self.timeout_config,
                trust_env=True if self.args.proxy else False,
                retries=self.args.retries,
                fallback_to_http=not self.args.disable_http_probe,
                fallback_retries=self.args.retries,
                backoff_strategy=BackoffStrategy.EXPONENTIAL,
                debug=self.args.debug
            )

            # FIX: Parse headers BEFORE Headless init so custom headers are available
            if self.args.header:
                for header_str in self.args.header:
                    try:
                        name, value = header_str.split(':', 1)
                        self.request_headers[name.strip()] = value.strip()
                    except ValueError:
                        self.logger.warn(f"Invalid header: '{header_str}'")

            # Headless (now receives populated request_headers)
            if self.args.screenshot:
                self.headlessclient = Headless(
                    True,
                    timeout=self.args.screenshot_timeout,
                    screenshot_path=self.args.screenshot_path,
                    save_pdf=self.args.save_pdf,
                    idle_time=self.args.screenshot_idle,
                    headers=self.request_headers,
                    full_page=True,
                    system_chrome_path=self.args.system_chrome_path,
                    chrome_options=self.generic.string_to_string_list(self.args.headless_options),
                    proxy=self.args.proxy,
                    random_agent=self.args.random_agent,
                    include_bytes=self.args.include_bytes,
                    verbose=self.args.verbose
                )

            # Parser
            self.resparser = Resparser(
                self.args,
                self.nameserver,
                self.generic.string_to_string_list(self.args.hash, ",")
            )

            if self.args.debug:
                self.logger.debug("Setup complete")

        except Exception as e:
            self.logger.error(f"Setup error: {e}")
            if self.args.debug:
                import traceback
                self.logger.error(traceback.format_exc())
            raise

    async def cleanup(self) -> None:
        """Cleanup resources. Idempotent — safe to call multiple times."""
        if getattr(self, '_cleaned_up', False):
            return
        self._cleaned_up = True

        try:
            if self.args.debug:
                self.logger.debug("Cleanup starting...")

            if self.requester:
                await self.requester.close()
            if self.connector:
                await self.connector.close()
            if self.args.screenshot and self.headlessclient:
                await self.headlessclient.close()
            if self.hmap:
                await self.hmap.close()
            if self.tmpdirpath and os.path.exists(self.tmpdirpath):
                await self.tempdir.close()
            if self.tmpresumepath and os.path.exists(self.tmpresumepath):
                await self.tempresume.close()
            if self.tmpfilepath and os.path.exists(self.tmpfilepath):
                await self.tempfile.close()

            if self.args.debug:
                self.logger.debug(f"Stats - Completed: {self._completed_tasks:,}, Failed: {self._failed_tasks:,}")

        except Exception as e:
            if self.args.debug:
                self.logger.debug(f"Cleanup error: {e}")

    def _detect_resume_marker(self) -> None:
        """Check if resume file is a JSON marker (new format) or old text file."""
        import json
        if not self.args.resume or not os.path.exists(self.args.resume):
            return
        try:
            with open(self.args.resume, 'r') as f:
                marker = json.load(f)
            if isinstance(marker, dict) and marker.get("version") == 1:
                self._resume_marker = marker
        except (json.JSONDecodeError, KeyError, IOError):
            pass  # Not a JSON marker — old text format, handled by existing code

    async def _setupIO(self) -> None:
        """Setup input source"""
        try:
            if self.args.url:
                urls = self.generic.string_to_string_list(self.args.url, ",")
                self.tmpfilepath = await self.tempfile.create()
                self.inputer = self.tmpfilepath
                for url in urls:
                    await self.tempfile.write(url + "\n")
                return

            if self.args.list:
                if not os.path.exists(self.args.list):
                    self.logger.warn(f"{self.args.list} not found")
                    await self.cleanup()
                    exit(1)
                self.inputer = self.args.list
                return

            if self.args.resume:
                if not os.path.exists(self.args.resume):
                    self.logger.warn(f"{self.args.resume} not found")
                    await self.cleanup()
                    exit(1)
                if self._resume_marker:
                    return  # Data already in persisted HMap, no inputer needed
                self.inputer = self.args.resume
                return

            if sys.stdin.isatty():
                self.logger.warn("No input provided")
                await self.cleanup()
                exit(1)
            else:
                urls = [d.strip() for d in sys.stdin if d.strip()]
                self.tmpfilepath = await self.tempfile.create()
                self.inputer = self.tmpfilepath
                for url in urls:
                    await self.tempfile.write(url + "\n")
                return
        except Exception as e:
            self.logger.error(f"Input error: {e}")
            if self.args.debug:
                import traceback
                self.logger.error(traceback.format_exc())

    def _extract_raw_host(self, line: str) -> Optional[str]:
        """Strip scheme, port, and path from input line, returning just the host/domain/IP.

        Examples:
            https://example.com:8080/path -> example.com
            http://1.2.3.4/api           -> 1.2.3.4
            example.com:443              -> example.com
            example.com                  -> example.com
            192.168.1.0/24               -> 192.168.1.0/24  (CIDR passthrough)
            [::1]:8080                   -> ::1
        """
        line = line.strip()
        if not line:
            return None

        # If it has a scheme, parse it to extract just the host
        if line.startswith(('http://', 'https://')):
            parsed = self._url_builder.parse_url(line)
            if parsed and parsed['host']:
                return parsed['host']
            return None

        # CIDR passthrough — don't strip anything
        if self.ip_utils.is_cidr(line):
            return line

        # host:port format — but be careful with bare IPv6 (multiple colons)
        if ':' in line:
            if line.count(':') == 1:
                # Simple host:port like example.com:443
                host_part = line.split(':')[0]
                return host_part if host_part else None
            # Multiple colons = likely bare IPv6, return as-is
            # Strip brackets if present: [::1] -> ::1
            if line.startswith('[') and ']' in line:
                return line[1:line.index(']')]
            return line

        return line

    async def _disk_load(self) -> None:
        """Load raw hosts into LevelDB disk cache with batch writes.

        Strips scheme/port from input, stores only raw hostnames/IPs.
        CIDR ranges are expanded. Deduplication via LevelDB + in-batch pending set.
        """
        if not self.args.stats:
            self.cache_bar = ProgressBar(None, "Loading")
            self.cache_bar.start()
        else:
            self.cache_logger = ProgressLogger(self.logger, None, "Loading")

        try:
            self.hmap.start_batch()

            async for line in self.fileutils.stream(self.inputer):
                if self._shutdown.is_set():
                    break

                if not line:
                    continue

                # For resume files, hosts are already raw — skip extraction
                if self.args.resume:
                    host = line.strip()
                else:
                    host = self._extract_raw_host(line)

                if not host:
                    continue

                if not self.args.resume and self.ip_utils.is_cidr(host):
                    async for ip in self.cidr_streamer.stream(host):
                        if self._shutdown.is_set():
                            break
                        if await self.hmap.batch_add(ip):
                            self.db_total += 1
                            if self.cache_bar:
                                self.cache_bar.update()
                            if self.cache_logger:
                                await self.cache_logger.update()
                else:
                    if await self.hmap.batch_add(host):
                        self.db_total += 1
                        if self.cache_bar:
                            self.cache_bar.update()
                        if self.cache_logger:
                            await self.cache_logger.update()

            # Flush remaining batch
            await self.hmap.flush_batch()

        finally:
            if self.cache_bar:
                try:
                    self.cache_bar.close()
                except RuntimeError:
                    pass

            if self.args.debug:
                self.logger.debug(f"Hosts loaded: {self.db_total:,}")

    async def _stream_ports(self) -> AsyncGenerator[int, None]:

        if self._ports_list:
            for port in self._ports_list:
                if self._shutdown.is_set():
                    return
                yield port
        elif self._port_file:
            async for line in self.fileutils.stream(self._port_file):
                if self._shutdown.is_set():
                    return
                if line.strip().isdigit():
                    yield int(line.strip())
        else:
            yield None

    async def _stream_paths(self) -> AsyncGenerator[str, None]:

        if self._paths_list:
            for path in self._paths_list:
                if self._shutdown.is_set():
                    return
                yield path
        elif self._path_file:
            async for line in self.fileutils.stream(self._path_file):
                if self._shutdown.is_set():
                    return
                if line.strip():
                    yield line.strip()
        else:
            yield None

    async def _targets_stream(self, host: str) -> AsyncGenerator[str, None]:
        """Generate URLs from a raw host by crossing with ports and paths."""
        if self.port_total > 0 and self.path_total > 0:
            async for port in self._stream_ports():
                if self._shutdown.is_set():
                    return
                async for path in self._stream_paths():
                    if self._shutdown.is_set():
                        return
                    url = self._url_builder.build('https', host, port, path)
                    yield url

        elif self.port_total > 0:
            async for port in self._stream_ports():
                if self._shutdown.is_set():
                    return
                url = self._url_builder.build('https', host, port, None)
                yield url

        elif self.path_total > 0:
            async for path in self._stream_paths():
                if self._shutdown.is_set():
                    return
                url = self._url_builder.build('https', host, None, path)
                yield url
        else:
            yield f'https://{host}'

    async def _tracked_expand(self, host: str) -> AsyncGenerator[tuple, None]:
        """Wrap _targets_stream to yield (host, url) tuples and count URLs per host."""
        async for url in self._targets_stream(host):
            self._host_pending[host] = self._host_pending.get(host, 0) + 1
            yield (host, url)

    async def _try_complete_host(self, host: str) -> None:
        """Delete host from HMap only when all URLs are submitted AND processed."""
        if self._shutdown.is_set():
            return
        if host in self._host_all_submitted and self._host_pending.get(host, 0) <= 0:
            await self.hmap.delete(host)
            self._host_pending.pop(host, None)
            self._host_all_submitted.discard(host)

    async def output_processor(self) -> None:
        try:
            while True:
                result = await self._output_chan.get()

                if result is None:
                    self._output_chan.task_done()
                    break

                url = result['url']
                results = result['results']

                try:
                    await self.resparser.resultsparser(results, url, self.args.output)
                except Exception as e:
                    if self.args.debug:
                        self.logger.debug(f"Output error {url}: {e}")

                self._output_chan.task_done()
        except Exception as e:
            if self.args.debug:
                self.logger.debug(f"Output processor error: {e}")

    async def _analyze(self, item) -> None:
        """Analyze a single URL. Called by WorkerPool workers.

        Receives (host, url) tuples from _tracked_expand.
        Rate limiting is handled by the WorkerPool, not here.
        Each call builds its own headers dict to avoid shared state between workers.
        """
        try:
            host, url = item

            # Build per-request headers — no shared dict mutation
            headers = dict(self.request_headers)
            headers["User-Agent"] = (
                self.httputils.get_random_user_agent()
                if self.args.random_agent
                else "git+Subprober/V2"
            )

            request_kwargs = {
                'headers': headers,
                'allow_redirects': self.args.allow_redirect,
                'max_redirects': self.args.max_redirection if self.args.allow_redirect else 0,
            }

            if self.args.proxy:
                request_kwargs['proxy'] = self.args.proxy
            if self.args.body:
                request_kwargs['data'] = self.args.body
            if self.args.sni_hostname:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                request_kwargs['ssl'] = ssl_context
                request_kwargs['server_hostname'] = self.args.sni_hostname

            try:
                async with self.requester.request(
                        self.args.method.upper(),
                        url,
                        **request_kwargs
                ) as response:
                    text = await response.text()
                    response_time = response.response_time

                    if not await self._apply_match_filter_conditions(
                            response,
                            text=text,
                            response_time=response_time
                    ):
                        return

                    results = await self.resparser.resparser(
                        response,
                        response.requested_url,
                        response.response_time
                    )

                    # FIX: operator precedence — was: full_output or tls and json
                    if (self.args.full_output or self.args.tls) and self.args.json:
                        if len(response.tlsinfo) > 0:
                            results["tls"] = response.tlsinfo

                    if self.args.screenshot:
                        results["headless"] = await self.headlessclient.capture(
                            response.requested_url
                        )

                    await self._output_chan.put({
                        'url': response.requested_url,
                        'results': results
                    })

                    self._completed_tasks += 1

            except Exception as e:
                self._failed_tasks += 1
                if self.args.debug:
                    self.logger.debug(f"Request failed {url}: {e}")

        except Exception as e:
            self._failed_tasks += 1
            if self.args.debug:
                self.logger.debug(f"Analyzer error: {e}")
        finally:
            if not self._shutdown.is_set():
                # Track per-host completion — delete from HMap when all URLs done
                try:
                    host_key = item[0] if isinstance(item, tuple) else None
                    if host_key is not None:
                        self._host_pending[host_key] -= 1
                        if self._host_pending[host_key] <= 0:
                            await self._try_complete_host(host_key)
                except Exception:
                    pass

                if self.probe_bar:
                    self.probe_bar.update()
                if self.probe_logger:
                    await self.probe_logger.update()

    def _sighandler(self) -> None:
        """Signal handler for CTRL+C"""
        if not self.args.silent:
            self.logger.warn("CTRL+C - graceful shutdown...")
        self._shutdown.set()

        loop = asyncio.get_event_loop()
        loop.create_task(self._handle_interrupt())

    async def _handle_interrupt(self):
        """Handle interrupt gracefully.

        NOTE: save_resume_file() is NOT called here — it's called in sprint()'s
        shutdown path, which runs BEFORE cleanup closes the HMap. If we tried
        to save here, sprint()'s finally block would race ahead and close/delete
        the HMap before we get a chance to save.
        """
        try:
            await asyncio.sleep(0.5)

            # Cancel worker pool if running
            if self.pool:
                await self.pool.cancel()

        except Exception as e:
            if self.args.debug:
                self.logger.debug(f"Interrupt error: {e}")
        finally:
            # Give sprint()'s finally block time to save resume + cleanup
            await asyncio.sleep(2.0)
            # Cancel remaining tasks for clean exit
            for task in asyncio.all_tasks():
                if task is not asyncio.current_task():
                    task.cancel()

    async def save_resume_file(self) -> None:
        """Save lightweight JSON resume marker pointing to persisted HMap.

        Instead of iterating all remaining hosts (slow for 1M+ hosts),
        we just persist the LevelDB directory and write a tiny JSON marker
        pointing to it. Resume load is instant: open existing LevelDB.
        """
        import json
        from datetime import datetime

        try:
            if self.probe_bar:
                try:
                    self.probe_bar.close()
                except RuntimeError:
                    pass

            if not self.hmap:
                return

            size = await self.hmap.size()

            if size == 0:
                if not self.args.silent:
                    self.logger.info("No remaining tasks")
                return

            filename = f"resume_{self.randomutils.random_string(8)}.cfg"

            marker = {
                "version": 1,
                "hmap_path": self.hmap.path,
                "created_at": datetime.now().isoformat(),
                "remaining": size,
                "total_loaded": self.db_total,
            }

            # Write marker FIRST — only detach (prevent cleanup) after write succeeds
            # so a failed write doesn't orphan the LevelDB directory on disk
            await self.fileutils.write(
                filename, content=json.dumps(marker, indent=2), mode="w"
            )

            # Marker written successfully — now prevent LevelDB directory deletion
            self.hmap.detach()

            if not self.args.silent:
                self.logger.info(f"Resume saved: {filename} ({size:,} remaining hosts)")

        except Exception as e:
            self.logger.error(f"Resume error: {e}")
            if self.args.debug:
                import traceback
                self.logger.error(traceback.format_exc())

    async def sprint(self) -> None:

        try:
            # Signal handler
            loop = asyncio.get_running_loop()
            try:
                loop.add_signal_handler(signal.SIGINT, self._sighandler)
            except Exception:
                pass

            # Detect resume marker before setup (need to know HMap path)
            self._detect_resume_marker()

            # Setup
            await self.setup()
            await self._setupIO()

            # Phase 1: LOAD — raw hosts into LevelDB with batch writes
            if self._resume_marker:
                # Resume: open existing LevelDB, rebuild size counter
                self.db_total = await self.hmap.rebuild_size()
                if not self.args.silent:
                    self.logger.info(f"Resumed: {self.db_total:,} hosts")
            else:
                await self._disk_load()

            if self.db_total == 0:
                self.logger.warn("No hosts loaded")
                await self.cleanup()
                return

            # Calculate total (for progress only)
            self.progress_total = self.db_total
            if self.port_total > 0:
                self.progress_total *= self.port_total
            if self.path_total > 0:
                self.progress_total *= self.path_total

            if self.args.debug:
                self.logger.debug(
                    f"Scan: {self.progress_total:,} URLs "
                    f"({self.db_total:,} hosts × {self.port_total or 1} ports × "
                    f"{self.path_total or 1} paths)"
                )

                if self.progress_total > 1_000_000:
                    self.logger.info(
                        f"Large scan: {self.progress_total:,} URLs. "
                    )

            # Progress tracking
            if not self.args.stats:
                self.probe_bar = ProgressBar(total=self.progress_total, title="Subprober")
                self.probe_bar.start()
            else:
                self.probe_logger = ProgressLogger(
                    self.logger,
                    total=self.progress_total,
                    title="Subprober"
                )

            self.task_started = True

            # Phase 2: PROBE — Go-style worker pool with backpressure
            output_task = asyncio.create_task(self.output_processor())

            self.pool = WorkerPool(
                num_workers=self.args.concurrency,
                queue_size=self.args.concurrency * 2,
                worker_func=self._analyze,
                rate_limiter=self.rate_limit,
            )
            await self.pool.start()

            # Fan-out: multiple producer coroutines expand hosts → URLs concurrently
            # Each producer takes a host, generates all its URLs, and submits them
            # to the shared worker pool queue (with backpressure).
            # max_producers scales with concurrency: enough to keep workers fed,
            # not so many that URL generation becomes a resource hog.
            max_producers = min(8, max(2, self.args.concurrency // 25))

            async def _on_host_submitted(host: str) -> None:
                """Called after all URLs for a host have been submitted to the queue."""
                self._host_all_submitted.add(host)
                await self._try_complete_host(host)

            await self.pool.fan_out(
                items_iter=self.hmap.iterkeys(),
                expand_func=self._tracked_expand,
                max_producers=max_producers,
                shutdown_event=self._shutdown,
                on_item_done=_on_host_submitted,
            )

            # Shutdown worker pool — drains queue, waits for all workers to finish
            if not self._shutdown.is_set():
                await self.pool.shutdown()
                self._host_pending.clear()
                self._host_all_submitted.clear()

            if self.args.debug:
                self.logger.debug("All analysis tasks complete")

            # Signal output processor to stop
            try:
                await self._output_chan.put(None)
                await output_task
            except (asyncio.CancelledError, Exception):
                pass

            if self.probe_bar:
                try:
                    self.probe_bar.close()
                except RuntimeError:
                    pass

            if not self.args.silent and self.args.debug:
                self.logger.info(
                    f"Complete - Done: {self.pool.completed_count:,}, "
                    f"Failed: {self.pool.failed_count:,}"
                )

            if self.args.debug:
                self.logger.debug("Scan finished successfully")

            # Clean up persisted HMap directory + marker file on successful completion
            if self._resume_marker and not self._shutdown.is_set():
                import shutil
                try:
                    hmap_path = self._resume_marker["hmap_path"]
                    # Close DB FIRST, then delete directory
                    if self.hmap:
                        await self.hmap.close()
                        self.hmap = None
                    if os.path.exists(hmap_path):
                        shutil.rmtree(hmap_path, ignore_errors=True)
                    if self.args.resume and os.path.exists(self.args.resume):
                        os.remove(self.args.resume)
                    if not self.args.silent:
                        self.logger.info("Resume state cleaned up (scan complete)")
                except Exception:
                    pass

        except Exception as e:
            self.logger.error(f"Sprint error: {e}")
            if self.args.debug:
                import traceback
                self.logger.error(traceback.format_exc())
        finally:
            # Save resume BEFORE cleanup closes HMap and deletes the LevelDB directory.
            # Shield against CancelledError from _handle_interrupt's task cancellation.
            if self._shutdown.is_set() and self.task_started:
                try:
                    await asyncio.shield(self.save_resume_file())
                except (asyncio.CancelledError, Exception):
                    pass
            await self.cleanup()
