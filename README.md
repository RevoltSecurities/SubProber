# Subprober - A Fast Multi-Purpose Http Probing Tool for Penetration Testing

![GitHub last commit](https://img.shields.io/github/last-commit/sanjai-AK47/Subprober) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/sanjai-AK47/Subprober) [![GitHub license](https://img.shields.io/github/license/sanjai-AK47/Subprober)](https://github.com/sanjai-AK47/Subprober/blob/main/LICENSE) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/d-sanjai-kumar-109a7227b/)

### Overview

Subprober  is a powerful and efficient tool designed for penetration testers and security professionals. This release introduces several enhancements, bug fixes, and new features to elevate your subdomain probing experience. Subprober facilitates fast and reliable information extraction, making it an invaluable asset for penetration testing workflows.

<h1 align="center">
  <img src="https://github.com/RevoltSecurities/SubProber/assets/119435129/98ec1073-e565-40a6-a76c-483d81a1a3d0" width="700px">
  <br>
</h1>

- Fast and configurable probings
- Supported Inputs: hosts, URLS, IPs
- Supports multiple methods http requests
- Supports proxies and customizable Header for probing
- Progress your probing tasks

### Features in V1.0.9:

- **New Probing configurations**

    - **-ip**   : **finds the ips of urls**
    - **-cn**   : **find the cname of urls**
    - **-maxr** : **maximum redirection for url**
    - **-ra**   : **enable random agent to probe with random agent**
    - **-X**    : **custom method for urls to probe**
    - **-H**    : **set custom header for urls to probe**
    - **-sc**   : **removed default to show response code and this flag to improve the subprober I/O**
    
- **Headless**

    - **-ss**   : **enable to probe and take screenshots for urls (required: chormedriver, geckodriver to be installed)**
    - **-st**   : **set a timeout value for urls to take screenshots**
    - **-bt**   : **select your browser type to take screenshots**

### Why Subprober:
 
Subprober is a http probing toolkit build in **python**, wait a minute? yes you read it right its build in python Which is high in concurrent to probe.
Hey wait its **python** and **Concurrent** how and what about **GIL**? Yes let me Explain you, Subprober utilized asynchronous performance which make 
subprober to perform concurrent probing and taking screenshots which nearly gives performance like **GOLANG!!!**, Yes performance like **Golang** in **python**
because it uses **uvloops** with **asynchronous** Libraries like **aiohttp**, **asyncio**, **arsenic**, **aiodns** by this, Subprober provide you more concurrent 
performance with high accuracy and Subprober is capable to handle high loads and ability to give high performance in even low end systems and also to your low end VPS 
without causing any high CPU loads even if it is high load of inputs to probe

### Subprober Probing Configuration:

| Probes               | Default check | Flags to Use                        |
|----------------------|---------------|-------------------------------------|
| Url                  | True          |                                     |
| Title                | True          | `-tl`,   `--title`                  |
| Status code          | True          | `-sc`,   `--status-code`            |
| Response Length      | true          | `-wc`.   `--word-count`             |
| Server               | True          | `-sv`,   `--server`                 |  
| Content Type         | True          | `-apt`,  `--application-type`       |
| Follow redirection   | False         | `-ar`,   `--allow-redirect`         |
| Path                 | False         | `-p`,    `--path`                   |
| Redirect location    | False         | `-l`,    `--location`               |
| Max redirect follow  | False         | `-maxr`, `--max-redirection`        |
| Disable http probe   | False         | `-dhp`,  `--disable-http-probe`     |
| Random user agents   | False         | `-ra`,   `--random-agent`           |
| Ipaddress of Host    | False         | `-ip`,   `--ipaddress`              |
| Cname of Host        | False         | `-cn`,   `--cname`                  |
| Proxy                | False         | `-px`,   `--proxy`                  |
| Custom Headers       | False         | `-H`,    `--header`                 |

### Subprober headless configurations:

1. **Requirement**: Subprober now offers a new headless screenshot feature, but before using it, you need to ensure you have the appropriate browser and driver installed. This feature supports both Chrome and Firefox browsers.

2. **Browser and Driver Compatibility**: It's crucial to match the versions of the browser and driver. If you're using Chrome, ensure that the installed Chromedriver version matches your Chrome browser version. The same applies if you're using Firefox and Geckodriver.

3. **Installation Guide**: If you're unsure how to install Chrome browser and Chromedriver there are helpful resources available. For example, you can refer to this [blog](https://katekuehl.medium.com/installation-guide-for-google-chrome-chromedriver-and-selenium-in-a-python-virtual-environment-e1875220be2f) for a step-by-step installation guide. It provides detailed instructions to set up Chrome browser and Chromedriver in system executable path

4. **Following the Guide**: Follow the guide carefully to ensure that you install the browser and driver correctly. It's essential to pay attention to version compatibility and to execute the installation steps accurately.

5. **Browser Selection**: Subprober allows users to choose their preferred browser type for taking screenshots. You can opt for either Chrome or Firefox, depending on your preference and requirements.

6. **Usage**: Once you've installed the browser and driver, you can configure Subprober to utilize the headless screenshot feature. Make sure to specify the browser type (Chrome or Firefox) and ensure that the versions are compatible.


### Installation

**To install Subprober you need python latest version to be installed and then you can follow the below steps to install subprober**

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



### License

Subprober is open-source software licensed under the GPL-3.0 License. See the [LICENSE](https://github.com/sanjai-AK47/Subprober/blob/main/LICENSE) file for details.

### Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to help improve Subprober.

### Author:
This tool is developed by [D.Sanjai Kumar](https://www.linkedin.com/in/d-sanjai-kumar-109a7227b/) for support the open source community for CyberSecurity and Ethical Hacking and
The Subprober is built for reconnaissance and ethical hacking purposes and developer is not responsible for any unethical purposes so
please use the Subprober with responsible and Ethically . Happy Hacking Hackers you can support my contribution by giving a ⭐ to the Subprober which motivate me to develop more like this ♥️.


