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
          
{bold}{white}Subprober - An essential HTTP multi-purpose Probing Tool for Penetration testers

{bold}[{bold}{blue}Description{reset}{bold}{white}]{reset} :

    {bold}{white}Subprober is a high-performance tool designed for probing and extract vital information efficiently.{reset}

{bold}[{bold}{blue}Options{reset}{bold}{white}]{reset}:{reset}{bold}{white}

    {bold}[{bold}{blue}INPUT{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -f,    --filename              specify the filename containing a list of urls for probing.                                       
        -u,    --url                   specify a target URL for direct probing
        stdin/stdout                   subprober supports both stdin/stdout and enable -nc to pipe the output of subprober
                                      
    {bold}[{bold}{blue}PROBES-CONFIG{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -sc,   --status-code           display the response status code
        -tl,   --title                 retrieve and display the titles
        -sv,   --server                identify and display the server name
        -wc,   --word-count            retrieve and display the content length
        -l ,   --location              display the redirected location of the response.
        -apt,  --application-type      determine and display the application type.
        -p,    --path                  specify a path for probe and get results ex: -p admin.php
        -px,   --proxy                 specify a proxy to send the requests through your proxy or BurpSuite (ex: http://127.0.0.1:8080)
        -gw,   --grep-word             enable The grep word flag will be usefull when grepping partiuclar status codes
        -ar,   --allow-redirect        enabling these flag will make Subprober to follow the redirection and ger results
        -dhp,  --disable-http-probe    disables the subprober from probing to http protocols and only for https when no protocol is specified
        -X  ,  --method                request methods to probe and get response
        -H  ,  --header                add a custom headers for probing and -H can be used multiple times to pass multiple header values (ex: -H application/json -H X-Forwarded-Host: 127.0.0.1)
        -ra ,  --random-agent          enable Random User-Agent to use for probing (default: subprober/Alpha)
        -ip ,  --ip                    find ip address for the host
        -cn ,  --cname                 find cname for the host
        -maxr, --max-redirection       set a max value to follow redirection (default: 10)
    
    {bold}[{bold}{blue}HEADLESS-Mode{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -ss,   --screenshot            enable to take screenshot of the page using headless browsers with asynchronous performance
        -st,   --screenshot-timeout    eet a timeout values for taking screenshosts  
        -br,   --browser-type          select a browser for taking screenshots and browser available: chrome, firefox (default: chrome)
                                       and requires chrome driver, gecko driver to be installed
    {bold}[{bold}{blue}MATCHERS{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -ex,   --exclude               exclude specific response status code(s) from the analysis.
        -mc,   --match                 specify specific response status code(s) to include in the analysis.
                                      
    {bold}[{bold}{blue}OUTPUT{reset}{bold}{white}]{reset}:{reset}{bold}{white}
    
        -o,    --output                define the output filename to store the results of the probing operation.
        -das,  ---disable-auto-save    disable the autosave of the results when no output file is specified.
        -oD,   --output-directory      define a folder name to save  screenshot outputs.

    {bold}[{bold}{blue}Rate-Limits{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -c,    --concurrency           set the concurrency level for subprober (default 50)
        -to,   --timeout               set a custom timeout value for sending requests.
        
    {bold}[{bold}{blue}UPDATES{reset}{bold}{white}]{reset}:{reset}{bold}{white}
        -up,   --update                update Subprober to the latest version (pip required to be installed)
        -sup,  --show-updates          shows the current version subprober updates 
    {bold}[{bold}{blue}DEBUG{reset}{bold}{white}]{reset}:{reset}{bold}{white}

        -h,    --help                  show this help message for you and exit!
        -s,    --silent                enable silent mode to suppress the display of Subprober banner and version information.
        -v,    --verbose               enable verbose mode to display error results on the console.
        -nc,   --no-color              enabling the --no-color will display the output without any CLI colors{reset}""")
    quit()