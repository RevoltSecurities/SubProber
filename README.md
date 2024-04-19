# Subprober v1.0.9 - A Fast Multi-Purpose Http Probing Tool for Penetration Testing

![GitHub last commit](https://img.shields.io/github/last-commit/sanjai-AK47/Subprober) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/sanjai-AK47/Subprober) [![GitHub license](https://img.shields.io/github/license/sanjai-AK47/Subprober)](https://github.com/sanjai-AK47/Subprober/blob/main/LICENSE) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/d-sanjai-kumar-109a7227b/)

### Overview

Subprober  is a powerful and efficient tool designed for penetration testers and security professionals. This release introduces several enhancements, bug fixes, and new features to elevate your subdomain probing experience. Subprober facilitates fast and reliable information extraction, making it an invaluable asset for penetration testing workflows.

### Features in V1.0.8:

- **New Probing configurations**

    - **-ip**   : **finds the ips of urls**
    - **-cn**   : **find the cname of urls**
    - **-maxr** : **maximum redirection for url**
    - **-ra**   : **enable random agent to probe with random agent**
    - **-X**    : **custom method for urls to probe**
    - **-H**    : **set custom header for urls to probe**
    - **-sc**   : **removed default to show response code and this flag to improve the subprober I/O**
    
- **Improved Concurrency**

    - **Subprober concurrency and accuracy are improved with asynchoronous libraries** `aiohttp`, `arsenic`, `aiodns` **which make subprober to asynchornously probe urls**
        
- **Headless**

    - **-ss**   : **enable to probe and take screenshots for urls (required: chormedriver, geckodriver to be installed)**
    - **-st**   : **set a timeout value for urls to take screenshots**
    - **-bt**   : **select your browser type to take screenshots**
    
- **IO Support**:

    - **Subprober now support stdout when using `-nc` flag which make subprober output to be piped and extend your automated workflows**
    - **Now Subprober automatically detect the stdin are connected or not and quits**
    - **Improved Subprober is now capable to handle high load urls and probe for it and tested with 4m+ urls**

- **Patched issues**:
    - **Fixed issue to probe urls when passing `u`, `--url`** by [@blackcodersec](https://github.com/sanjai-AK47/SubProber/issues/4)
    - **Fixed double appendence of path when using `-p`, `--path`**
    - **Fixed update issue in previous version**
    - **Fixed issue in saving scrennshots output when urls passed with `-p`, `--path`**

### Speed and Loads:
Subprober is really concurrent in probing and taking screenshots asynchornously and speed may differ depends on your network
subprober can be used even in your  less sources `aws` VPS server without causing any high load to your system but only when probing
but not when taking screenshots, ip, cnames and Subprober can handle high load of urls and subprober tested with 2m+ urls and probed
without any problem, users can also try more urls than tested

### Installation and Updates

##### Method 1:

```bash
pip install git+https://github.com/sanjai-AK47/Subprober.git
subprober -h
```

#### Method 2:

```bash
git clone https://github.com/sanjai-AK47/SubProber.git
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
                                                         
                
                
                    @RevoltSecurities

          
Subprober - An essential HTTP multi-purpose Probing Tool for Penetration testers

[Description] :

    Subprober is a high-performance tool designed for probing and extract vital information efficiently.

[Options]:

    [INPUT]:

        -f,    --filename              specify the filename containing a list of urls for probing.                                       
        -u,    --url                   specify a target URL for direct probing
        stdin/stdout                   subprober supports both stdin/stdout and enable -nc to pipe the output of subprober
                                      
    [PROBES-CONFIG]:

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
    
    [HEADLESS-Mode]:

        -ss,   --screenshot            enable to take screenshot of the page using headless browsers with asynchronous performance
        -st,   --screenshot-timeout    eet a timeout values for taking screenshosts  
        -br,   --browser-type          select a browser for taking screenshots and browser available: chrome, firefox (default: chrome)
                                       and requires chrome driver, gecko driver to be installed
    [MATCHERS]:

        -ex,   --exclude               exclude specific response status code(s) from the analysis.
        -mc,   --match                 specify specific response status code(s) to include in the analysis.
                                      
    [OUTPUT]:
    
        -o,    --output                define the output filename to store the results of the probing operation.
        -das,  ---disable-auto-save    disable the autosave of the results when no output file is specified.
        -oD,   --output-directory      define a folder name to save  screenshot outputs.

    [Rate-Limits]:

        -c,    --concurrency           set the concurrency level for subprober (default 50)
        -to,   --timeout               set a custom timeout value for sending requests.
        
    [UPDATES]:
        -up,   --update                update Subprober to the latest version (pip required to be installed)
        -sup,  --show-updates          shows the current version subprober updates 
    [DEBUG]:

        -h,    --help                  show this help message for you and exit!
        -s,    --silent                enable silent mode to suppress the display of Subprober banner and version information.
        -v,    --verbose               enable verbose mode to display error results on the console.
        -nc,   --no-color              enabling the --no-color will display the output without any CLI colors

```

#### Basic Usage

```bash
subprober -f subdomains.txt -o output.txt -tl -wc -sv  -apt -wc -ex 500 -v -o output.txt -c 20
```

### Direct URL Probing

```bash
subprober -u https://example.com -c 20 -to 8 -tl -sv -wc -apt -ex 500 -o output.txt
```

### Pipe Subdomains, Domains & ips

```bash
cat subdomains.txt | subprober -c 20 -to 8 -tl -sv -wc -apt -ex 50 -o output.txt
```

### License

Subprober is open-source software licensed under the GPL-3.0 License. See the [LICENSE](https://github.com/sanjai-AK47/Subprober/blob/main/LICENSE) file for details.

### Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to help improve Subprober.


### Sample Usage of Subprober:
![Screenshot from 2023-11-12 19-00-28](https://github.com/sanjai-AK47/SubProber/assets/119435129/2403d849-c91f-4d09-92f5-8314ae1a18ef)

### Information:
This tool is developed by [D.Sanjai Kumar](https://www.linkedin.com/in/d-sanjai-kumar-109a7227b/) for support the open source community for CyberSecurity and Ethical Hacking and
The Subprober is built for reconnaissance and ethical hacking purposes and developer is not responsible for any unethical purposes so
please use the Subprober with responsible and Ethically . Happy Hacking Hackers you can support my contribution by giving a ⭐ to the Subprober which motivate me to develop more like this ♥️.


