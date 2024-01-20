# Subprober v1.0.5 - Fast Probing Tool for Penetration Testing

![GitHub last commit](https://img.shields.io/github/last-commit/sanjai-AK47/Subprober) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/sanjai-AK47/Subprober) [![GitHub license](https://img.shields.io/github/license/sanjai-AK47/Subprober)](https://github.com/sanjai-AK47/Subprober/blob/main/LICENSE) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/d-sanjai-kumar-109a7227b/)

### Overview

Subprober v1.0.5 is a powerful and efficient tool designed for penetration testers and security professionals. This release introduces several enhancements, bug fixes, and new features to elevate your subdomain probing experience. Subprober facilitates fast and reliable information extraction, making it an invaluable asset for penetration testing workflows.

### Features in V1.0.5:
- Subprober Concurrency and Accuracy are Improved with libraries like aiohttp,asyncio
- Subprober Error handling and Synchronization are improved
- Resolved some Bugs for Subprober
- Subprober Commands are changed with usefull flags
- Resolved executive errors in v1.0.4
- Subprober requires python version 3.11.x

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
### update to v1.0.4 to v1.04.5:

```bash
pip install git+https://github.com/sanjai-AK47/Subprober.git
subprober -h
```


### Recommended Concurrencies:

**Info:** Subprober is improved with higher concurrency and accuracy for probings and recommend the users to use the concurrencies less which is efficient and accurate for probing
  - 30-50   : this range of concurrency can be given when probing for more than 50K+ Subdomains, ips, domains etc..
  - 50-80   : this range of concurrency can be given when probing for more than 100K+ Subdomains, ips, domains etc..
  - 100-120 : this range of concurrency can be given when probing for more than 150K+ Subdomains, ips, domains etc..

Note higher concurrency values may results in inaccurate results because subprober builded with higher concurrency and more accurate than other probing tool with following mentioned concurrency values

### Usage

```yaml

   _____       __    ____             __             
  / ___/__  __/ /_  / __ \_________  / /_  ___  _____
  \__ \/ / / / __ \/ /_/ / ___/ __ \/ __ \/ _ \/ ___/
 ___/ / /_/ / /_/ / ____/ /  / /_/ / /_/ /  __/ /    
/____/\__,_/_.___/_/   /_/   \____/_.___/\___/_/     
                                                         
                
                
                    Author : D.Sanjai Kumar @CyberRevoltSecurities

                                                                         
                                                  

          
Subprober - An essential HTTP multiple Probing Tool for Penetration testers and Bug Bounty Hunters

[Description] :

    Subprober is a high-performance tool designed for probing and  extract vital information efficiently.

[Flags]:

    -f,   --filename              Specify the filename containing a list of subdomains for targeted probing. 
                                 This flag is used to find and analyze status codes and other pertinent details.
                      
    -h,   --help                Show this help message for you and exit!
    
    -u,   --url                 Specify a target URL for direct probing. This flag allows for the extraction of 
                                 status codes and other valuable information.

    -o,   --output              Define the output filename to store the results of the probing operation.

    -c,   --concurrency          Set the concurrency level for multiple processes. Default is 10.

    -tl,  --title                Retrieve and display the title of subdomains.

    -to,  --timeout              Set a custom timeout value for sending requests.

    -sv,  --server               Identify and display the server information associated with subdomains.

    -wc,  --word-count           Retrieve and display the content length of subdomains.

    -apt, --application-type     Determine and display the application type of subdomains.

    -ex,  --exclude              Exclude specific response status code(s) from the analysis.

    -mc,  --match                Specify specific response status code(s) to include in the analysis.

    -s,   --silent               Enable silent mode to suppress the display of Subprober banner and version information.

    -v,   --verbose              Enable verbose mode to display error results on the console.
    
    -p,   --path                 Specify a path for probe and get results ex:: -p admin.php
    
    -px,  --proxy                Specify a proxy to send the requests through your proxy or BurpSuite ex: 127.0.0.1:8080
    
    -gw,  --grep-word            Enable The grep word flag will be usefull when grepping partiuclar codes like for 200: OK ---> cat subprober-results.txt | grep OK 
                                 This will show the results with 200-299 range codes
                                 
    -ar,  --allow-redirect       Enabling these flag will make Subprober to follow the redirection and ger results
    
    -nc,  --no-color             Enabling the --no-color will display the output without any CLI colors

    -up,  --update               Update Subprober to the latest version through pip and git.
    
[INFO]:

    subprober -f filename.txt -c 20 --title --server --application-type --word-count -o output.txt
    
    cat subdomains.txt | subprober -c 20 -to 8 -tl -sv -wc -apt -ex 404 500  -o output.txt
    
[NOTE]:


    - Important Note Subprober new version is highly built in with concurrent so please be sure with your concurrency value
      because high concurrency values will cause race condition.
      
    - Subprobers recommended concurrency value is between the range from 15-100 for accuracy and high concurrent performance.

```

#### Basic Usage

```bash
subprober -f subdomains.txt -o output.txt -tl -wc -sv  -apt -wc -ex 500 -v -o output.txt -c 20
```

### Direct URL Probing

```bash
subprober -u https://example.com -c 20 -to 8 -tl -sv -wc -apt -ex 500 -o output.txt
```

### Piping Subdomains

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


