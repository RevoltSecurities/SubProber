# Subprober 
An essential HTTP multi-purpose Probing Tool for Penetration Testers and Security Researchers with Asynchronous httpx client support

![GitHub last commit](https://img.shields.io/github/last-commit/RevoltSecurities/Subprober) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/RevoltSecurities/Subprober) [![GitHub license](https://img.shields.io/github/license/RevoltSecurities/Subprober)](https://github.com/RevoltSecurities/Subprober/blob/main/LICENSE) 

### Overview

Subprober  is a powerful and efficient tool designed for penetration testers and security professionals. This release introduces several enhancements, bug fixes, and new features to elevate your probing experience. Subprober facilitates fast and reliable information extraction, making it an invaluable asset for penetration testing workflows.

<h1 align="center">
  <img src="https://github.com/RevoltSecurities/SubProber/assets/119435129/5b763884-6bb2-4881-9005-2cfc9b3a0d35" width="700px">
  <br>
</h1>

- Fast and configurable probings
- Supported Inputs: hosts, URLS, IPs
- Supports multiple methods http requests
- Supports proxies and customizable Header for probing
- Progress your probing tasks


### Subprober Probing Configuration:

| Probes               | Default Check | Probes                  | Default Check |
|----------------------|---------------|-------------------------|---------------|
| Url                  | True          | UrlScheme               | False         |
| Title                | True          | Ports                   | False         |
| Status code          | True          | Paths                   | False         |
| Response Length      | True          | HTTP2                   | False         |
| Server               | True          | Response Body Hash      | False         |  
| Content Type         | True          | HTTP Version            | True          |
| Follow redirection   | False         | HTTP Method             | True          |
| Path                 | False         | Body Preview            | True          |
| Redirect location    | False         | Redirect History        | True          |
| Max redirection      | False         | Response Reason         | True          |
| IP address of Host   | False         | Word Count              | True          |
| Cname of Host        | False         | AAAA Record of Host     | False         |
| Jarm                 | False         | Response Time           | True          |
| Web Socket           | True          | Line Count              | True          |
| TLS Data             | False         | Redirect Location       | True          |



### Installation

**To install Subprober you need python latest version to be installed and then you can follow the below steps to install subprober**

**PIP Installation:**

```bash
pip install git+https://github.com/RevoltSecurities/Subprober.git
subprober -h
```

**PIPX Installation:**
```bash
pipx install git+https://github.com/RevoltSecurities/Subprober.git
subprober -h
```

**GIT Installation:**
```bash
git clone https://github.com/RevoltSecurities/SubProber.git
cd Subprober
pip install .
subprober -h
```


### Usage

```yaml
subprober -h      

   _____       __    ____             __             
  / ___/__  __/ /_  / __ \_________  / /_  ___  _____
  \__ \/ / / / __ \/ /_/ / ___/ __ \/ __ \/ _ \/ ___/
 ___/ / /_/ / /_/ / ____/ /  / /_/ / /_/ /  __/ /    
/____/\__,_/_.___/_/   /_/   \____/_.___/\___/_/     
                                                         
                
                
                    - RevoltSecurities


Subprober - An essential HTTP multi-purpose Probing Tool for Penetration Testers and Security Researchers with Asynchronous httpx client support

[Description] :

    Subprober is a high-performance tool designed for probing and extracting vital information efficiently with Asynchronous concurrency performance

[Options]:

    [INPUT]:

        -f,    --filename               specify the filename containing a list of Urls to probe                                       
        -u,    --url                    specify a Url to probe and supports comma-separated values (-u google.com,https://hackerone.com)
        stdin/stdout                    subprober supports both stdin/stdout and enables -nc to pipe the output of subprober
                                      
    [PROBES]:

        -sc,    --status-code           display the status code of the host
        -tl,    --title                 display the title of host
        -sv,    --server                display the server name of the host
        -wc,    --word-count            display the HTTP response word count
        -lc,    --line-count            display the HTTP response line count
        -cl,    --content-length        display the HTTP response content length
        -l ,    --location              display the redirected location of the host
        -apt,   --application-type      display the content type of the host
        -ip,    --ipaddress             display the IPs of the host
        -cn,    --cname                 display the CNAMEs of the host
        -aaa,   --aaa-records           display the AAAA records of the host
        -htv,   --http-version          display the server supported HTTP version of the host
        -hrs,   --http-reason           display the reason for HTTP connection of the host
        -jarm,  --jarm-fingerprint      display the JARM fingerprint hash of the host
        -rpt,   --response-time         display the response time for the successful request
        -wss,   --websocket             display the server supports websockets
        -hash,  --hash                  display response body in hash format (supported hashes: md5, mmh3, simhash, sha1, sha256, sha512)
        -dmt,   --display-method        display the method of the HTTP request 
        -bp,    --body-preview          display the HTTP response body in first n number of characters (default: 100)
    
    [CONFIG]:

        -dhp,   --disable-http-probe    disables subprober from probing HTTP protocols and only for HTTPS when no protocol is specified
        -X,     --method                request methods to probe and get response (supported: get, post, head, put, delete, patch, trace, connect, options) (default: get)
        -H,     --header                add custom headers for probing and -H can be used multiple times to pass multiple header values (ex: -H application/json -H X-Forwarded-Host: 127.0.0.1)
        -ra,    --random-agent          enable Random User-Agent to use for probing and applies same to screenshots. (default: subprober/Alpha)
        -px,    --proxy                 specify a proxy to send the requests through it (ex: http://127.0.0.1:8080)
        -ar,    --allow-redirect        enable following redirections
        -maxr,  --max-redirection       set max value to follow redirections (default: 10)
        -http2, --http2                 enable to request with HTTP/2 support (default: Http/1.1)
        -sni,   --sni-hostname          set custom TLS SNI host name for requests.
        
    [MISCELLANEOUS]:
    
        -p,     --path                  specify a path or text file of paths for probing and getting results (example: -p admin.php or -p paths.txt)
        -pt,    --port                  set custom port for making HTTP request and default ports are 80,443 based on the url scheme
        -tls,   --tls                   grabs the TLS data for the requested host
    
    [HEADLESS]:

        -ss,    --screenshot            enable to take screenshots of the page using headless browsers with asynchronous performance
        -st,    --screenshot-timeout    set a timeout value for taking screenshots (default: 15) 
        -scp,   --system-chrome-path    specify the executable path of the chromedriver to use system chrome to take screenshots
        -pdf,   --save-pdf              enable to save the screenshot image in the pdf format (default: png)
        -HH ,   --screenshot-headers    add custom headers for authenticated screenshots
        -icb,   --include-bytes         enable to include the screenshot bytes in output when json output enabled
        -hos,   --headless-options      set additional chrome headless browser options and supports comma-separated values (-ho "--start-maximized")
        -sid,   --screenshot-idle       set custom idle time in seconds before taking screenshots (default: 1)
        -sp,    --screenshot-path       specify a directory path to store screenshot results (default: currentdir/screenshots)
                                       
    [MATCHERS]:

        -mc,    --match-code            match http response by specified status codes and supports comma-separated values (-mc 200,302)
        -mcr,   --match-code-range      match http response by specified status code range and supports single value (-mcr 200-299)
        -ms,    --match-string          match http response containing the specified string and supports comma-separated values (-ms admin,login)
        -mr,    --match-regex           match http response matching the specified regex and supports comma-separated values (-mr .*admin.*,.*login.*)
        -mpt,   --match-path            match http response by URL path and supports comma-separated values (-mpt /admin/wp-ajax.php,/wp-json)
        -ml,    --match-length          match http response by specified response length and supports comma-separated values (-ml 1024,2048)
        -mlc,   --match-line-count      match http response by specified response line count and supports comma-separated values (-mlc 10,50)
        -mwc,   --match-word-count      match http response by specified word count and supports comma-separated values (-mwc 100,500)
        -mrt,   --match-response-time   match http response exceeding the specified minimum response time in seconds (-mrt 2.30)

    [FILTERS]:

        -fc,    --filter-code           filter http response by specified status codes and supports comma-separated values (-fc 404,500)
        -fcr,   --filter-code-range     filter http response by specified status code range and supports single value (-fcr 400-499)
        -fs,    --filter-string         filter http response containing the specified string and supports comma-separated values (-fs error,not found)
        -fr,    --filter-regex          filter http response matching the specified regex and supports comma-separated values (-fr .*admin.*,.*login.*)
        -fpt,   --filter-path           filter http response by URL path and supports comma-separated values (-fpt /error,404.html)
        -fl,    --filter-length         filter http response by specified response length and supports comma-separated values (-fl 1024,2048)
        -flc,   --filter-line-count     filter http response by specified response line count and supports comma-separated values (-flc 10,50)
        -fwc,   --filter-word-count     filter http response by specified response word count and supports comma-separated values (-fwc 100,500)
        -frt,   --filter-response-time  filter http response exceeding the specified maximum response time in seconds (-frt 2.30)

    [OUTPUT]:
    
        -o,     --output                define the output filename to store the results of the probing operation.
        -das,   --disable-auto-save     disable the auto-save of results when no output file is specified.
        -J,     --json                  store and display output in JSON format (includes only data from enabled options).
        -rdu,   --redirect-urls         display the redirect URLs in the output (requires -J and -ar to enabled to enabled).
        -rdh,   --redirect-history      display the full redirect history (requires -J and -ar to enabled).
        -rsc,   --redirect-status-codes display the status codes for redirections (requires -J and -ar to enabled).
        -rqh,   --request-headers       include request headers in the output (requires -J and -ar to enabled).
        -rsh,   --response-headers      include response headers in the output (requires -J and -ar to enabled).
        -fo,    --full-output           include all available data in the output (requires -J to enabled and doesn't overrides websocket,jarm,hashes options).

    [RATE-LIMIT]:

        -c,     --concurrency           set the concurrency level for sending http requests (default: 100)
        -rtl,   --rate-limit            set a rate limit for sending a maximum number of requests per second (default: 1000)
        -sct,   --screenshot-threads    set a threads level for taking screenshots (default: 40)
        
    [Optimization]:
    
        -to,    --timeout               set a custom timeout value for sending requests.
        -d,     --delay                 set a delay in seconds before sending each request (default: 0.5)
        -rts,   --retries               set a number of retries if a request fails to connect (default: 0)
        
    [UPDATES]:
    
        -up,    --update                update subprober to the latest version (pip required to be installed)
        -sup,   --show-updates          display the current or latest version of subprober updates 
        
    [DEBUG]:

        -h,     --help                  display this help message and exit!
        -s,     --silent                enable silent mode to suppress the display of Subprober banner and version information.
        -v,     --verbose               enable verbose mode to display error results on the console.
        -nc,    --no-color              enable to display the output without any CLI colors
```


### About:

The **SubProber** is a cutting-edge tool developed by **RevoltSecurities** to empower Security Researchers and Penetration Testers. Designed with efficiency and precision in mind, SubProber streamlines reconnaissance and enhances vulnerability detection. Released under the MIT License, it reflects our commitment to fostering innovation and collaboration within the open-source community.  

At **RevoltSecurities**, we aim to support researchers by providing advanced automation tools that simplify complex tasks, enabling professionals to focus on securing modern infrastructures.

