class Settings:
    def __init__(self, args):
        # INPUT Section
        self.list = args.list
        self.url = args.url
        self.resume = args.resume

        # PROBES Section
        self.status_code = args.status_code
        self.title = args.title
        self.server = args.server
        self.word_count = args.word_count
        self.line_count = args.line_count
        self.content_length = args.content_length
        self.location = args.location
        self.application_type = args.application_type
        self.ipaddress = args.ipaddress
        self.cname = args.cname
        self.aaaa_records = args.aaaa_records
        self.http_version = args.http_version
        self.http_reason = args.http_reason
        self.jarm_fingerprint = args.jarm_fingerprint
        self.response_time = args.response_time
        self.websocket = args.websocket
        self.hash = args.hash
        self.display_method = args.display_method
        self.body_preview = args.body_preview
        self.body = args.body
        self.resolvers = args.resolvers

        # CONFIG Section
        self.disable_http_probe = args.disable_http_probe
        self.method = args.method
        self.header = args.header
        self.random_agent = args.random_agent
        self.proxy = args.proxy
        self.allow_redirect = args.allow_redirect
        self.max_redirection = args.max_redirection
        self.http2 = args.http2
        self.sni_hostname = args.sni_hostname
        self.stats = args.stats

        # MISCELLANEOUS Section
        self.path = args.path
        self.port = args.port
        self.tls = args.tls

        # HEADLESS Section
        self.screenshot = args.screenshot
        self.screenshot_timeout = args.screenshot_timeout
        self.system_chrome_path = args.system_chrome_path
        self.save_pdf = args.save_pdf
        self.no_full_page = args.no_full_page
        self.include_bytes = args.include_bytes
        self.headless_options = args.headless_options
        self.screenshot_idle = args.screenshot_idle
        self.screenshot_path = args.screenshot_path

        # MATCHERS Section
        self.match_code = args.match_code
        self.match_code_range = args.match_code_range
        self.match_string = args.match_string
        self.match_regex = args.match_regex
        self.match_path = args.match_path
        self.match_length = args.match_length
        self.match_line_count = args.match_line_count
        self.match_word_count = args.match_word_count
        self.match_response_time = args.match_response_time

        # FILTERS Section
        self.filter_code = args.filter_code
        self.filter_code_range = args.filter_code_range
        self.filter_string = args.filter_string
        self.filter_regex = args.filter_regex
        self.filter_path = args.filter_path
        self.filter_length = args.filter_length
        self.filter_line_count = args.filter_line_count
        self.filter_word_count = args.filter_word_count
        self.filter_response_time = args.filter_response_time

        # OUTPUT Section
        self.output = args.output
        self.json = args.json
        self.redirect_urls = args.redirect_urls
        self.redirect_history = args.redirect_history
        self.redirect_status_codes = args.redirect_status_codes
        self.request_headers = args.request_headers
        self.response_headers = args.response_headers
        self.full_output = args.full_output

        # RATE-LIMIT Section
        self.concurrency = args.concurrency
        self.rate_limit = args.rate_limit

        # OPTIMIZATION Section
        self.timeout = args.timeout
        self.delay = args.delay
        self.retries = args.retries

        # UPDATES Section
        self.update = args.update
        self.show_updates = args.show_updates

        # DEBUG Section
        self.help = args.help
        self.silent = args.silent
        self.verbose = args.verbose
        self.no_color = args.no_color
        self.debug = args.debug

    def __repr__(self):
        """String representation of Settings."""
        return f"Settings(url={self.url}, concurrency={self.concurrency}, verbose={self.verbose})"

    def to_dict(self):
        """Convert settings to dictionary."""
        return {
            "filename": self.filename,
            "url": self.url,
            "resume": self.resume,

            "status_code": self.status_code,
            "title": self.title,
            "server": self.server,
            "word_count": self.word_count,
            "line_count": self.line_count,
            "content_length": self.content_length,
            "location": self.location,
            "application_type": self.application_type,
            "ipaddress": self.ipaddress,
            "cname": self.cname,
            "aaa_records": self.aaaa_records,
            "http_version": self.http_version,
            "http_reason": self.http_reason,
            "jarm_fingerprint": self.jarm_fingerprint,
            "response_time": self.response_time,
            "websocket": self.websocket,
            "hash": self.hash,
            "display_method": self.display_method,
            "body_preview": self.body_preview,
            "body": self.body,
            "resolvers": self.resolvers,

            "disable_http_probe": self.disable_http_probe,
            "method": self.method,
            "header": self.header,
            "random_agent": self.random_agent,
            "proxy": self.proxy,
            "allow_redirect": self.allow_redirect,
            "max_redirection": self.max_redirection,
            "http2": self.http2,
            "sni_hostname": self.sni_hostname,

            "path": self.path,
            "port": self.port,
            "tls": self.tls,

            "screenshot": self.screenshot,
            "screenshot_timeout": self.screenshot_timeout,
            "system_chrome_path": self.system_chrome_path,
            "save_pdf": self.save_pdf,
            "no_full_page": self.no_full_page,
            "include_bytes": self.include_bytes,
            "headless_options": self.headless_options,
            "screenshot_idle": self.screenshot_idle,
            "screenshot_path": self.screenshot_path,

            "match_code": self.match_code,
            "match_code_range": self.match_code_range,
            "match_string": self.match_string,
            "match_regex": self.match_regex,
            "match_path": self.match_path,
            "match_length": self.match_length,
            "match_line_count": self.match_line_count,
            "match_word_count": self.match_word_count,
            "match_response_time": self.match_response_time,

            "filter_code": self.filter_code,
            "filter_code_range": self.filter_code_range,
            "filter_string": self.filter_string,
            "filter_regex": self.filter_regex,
            "filter_path": self.filter_path,
            "filter_length": self.filter_length,
            "filter_line_count": self.filter_line_count,
            "filter_word_count": self.filter_word_count,
            "filter_response_time": self.filter_response_time,

            "output": self.output,
            "json": self.json,
            "redirect_urls": self.redirect_urls,
            "redirect_history": self.redirect_history,
            "redirect_status_codes": self.redirect_status_codes,
            "request_headers": self.request_headers,
            "response_headers": self.response_headers,
            "full_output": self.full_output,

            "concurrency": self.concurrency,
            "rate_limit": self.rate_limit,

            "timeout": self.timeout,
            "delay": self.delay,
            "retries": self.retries,

            "update": self.update,
            "show_updates": self.show_updates,

            "help": self.help,
            "silent": self.silent,
            "verbose": self.verbose,
            "no_color": self.no_color,
            "secret_debug": self.debug
        }