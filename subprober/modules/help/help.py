from colorama import Fore,Style
red =  Fore.RED
green = Fore.GREEN
magenta = Fore.MAGENTA
cyan = Fore.CYAN
mixed = Fore.RED + Fore.BLUE
blue = Fore.BLUE
yellow = Fore.YELLOW
white = Fore.WHITE
reset = Style.RESET_ALL
bold = Style.BRIGHT
colors = [ green, cyan, blue]

def __help__():
    
    print(f"""
          
{bold}{white}Subprober - An essential HTTP multi-purpose Probing Tool for Penetration Testers and Security Researchers with Asynchronous httpx client support

{bold}[{bold}{blue}Description{reset}{bold}{white}]{reset} :

    {bold}{white}Subprober is a high-performance tool designed for probing and extract vital information efficiently with Asynchronous concurrency performance{reset}

{bold}[{bold}{blue}Options{reset}{bold}{white}]{reset}:{reset}{bold}{white}

    {bold}[{bold}{blue}INPUT{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -f,    --filename              specify the filename containing a list of urls for probing.                                       
        -u,    --url                   specify a target URL for direct probing
        stdin/stdout                   subprober supports both stdin/stdout and enable -nc to pipe the output of subprober
                                      
    {bold}[{bold}{blue}PROBES-CONFIG{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -sc,    --status-code           display the status code of the host
        -tl,    --title                 display the title of host
        -sv,    --server                display the server name of the host
        -wc,    --word-count            display the content length of host
        -l ,    --location              display the redirected location of the host
        -apt,   --application-type      display the content type of the host
        -p,     --path                  specify a path for probe and get results (example: -p admin.php)
        -px,    --proxy                 specify a proxy to send the requests through your proxy (ex: http://127.0.0.1:8080)
        -gw,    --grep-word             enable The grep word flag will be usefull when grepping particular status codes
        -ar,    --allow-redirect        enable  to follow the redirections
        -dhp,   --disable-http-probe    disables the subprober from probing to http protocols and only for https when no protocol is specified
        -X  ,   --method                request methods to probe and get response (supported: get, post, head, put, delete, patch, trace, connect, options) (default: get)
        -H  ,   --header                add a custom headers for probing and -H can be used multiple times to pass multiple header values (ex: -H application/json -H X-Forwarded-Host: 127.0.0.1)
        -ra ,   --random-agent          enable Random User-Agent to use for probing (default: subprober/Alpha)
        -ip ,   --ip                    display the ip of the host
        -cn ,   --cname                 display the cname of the host
        -maxr,  --max-redirection       set a max value to follow redirection (default: 10)
        -http2, --http2                 enable to request with http2 support (default: Http/1.1)
        -htv,   --http-version          display the server supported http version of the host
        -hrs,   --http-reason           display the reason for http connection of the host
        -jarm,  --jarm-fingerprint      display the jarm figerprint hash of the host
    
    {bold}[{bold}{blue}HEADLESS-Mode{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -ss,   --screenshot            enable to take screenshot of the page using headless browsers with asynchronous performance
        -st,   --screenshot-timeout    set a timeout values for taking screenshosts  
        -br,   --browser-type          select a browser for taking screenshots and browser available: chrome, firefox (default: chrome)
                                       and requires chrome driver, gecko driver to be installed
                                       
    {bold}[{bold}{blue}MATCHERS{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -ex,   --exclude               exclude specific response status code(s) from the analysis (example: -ex 404 403)
        -mc,   --match                 specify specific response status code(s) to include in the analysis (example: -mc 200 302)
                                      
    {bold}[{bold}{blue}OUTPUT{reset}{bold}{white}]{reset}:{reset}{bold}{white}
    
        -o,    --output                define the output filename to store the results of the probing operation.
        -das,  ---disable-auto-save    disable the autosave of the results when no output file is specified.
        -oD,   --output-directory      define a folder name to save  screenshot outputs.

    {bold}[{bold}{blue}Rate-Limits{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -c,    --concurrency           set the concurrency level for subprober (default 50)
        -to,   --timeout               set a custom timeout value for sending requests.
        
    {bold}[{bold}{blue}UPDATES{reset}{bold}{white}]{reset}:{reset}{bold}{white}
    
        -up,   --update                update subprober to the latest version (pip required to be installed)
        -sup,  --show-updates          display the current or latest version subprober updates 
        
    {bold}[{bold}{blue}DEBUG{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -h,    --help                  display this help message for you and exit!
        -s,    --silent                enable silent mode to suppress the display of Subprober banner and version information.
        -v,    --verbose               enable verbose mode to display error results on the console.
        -nc,   --no-color              enabling the --no-color will display the output without any CLI colors{reset}""")
    exit()