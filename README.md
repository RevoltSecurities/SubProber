# Subprober v1.0.3 - Fast Probing Tool for Penetration Testing

![GitHub last commit](https://img.shields.io/github/last-commit/sanjai-AK47/Subprober) ![GitHub release (latest by date)](https://img.shields.io/github/v/release/sanjai-AK47/Subprober) [![GitHub license](https://img.shields.io/github/license/sanjai-AK47/Subprober)](https://github.com/sanjai-AK47/Subprober/blob/main/LICENSE) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/d-sanjai-kumar-109a7227b/)

### Overview

Subprober v1.0.3 is a powerful and efficient tool designed for penetration testers and security professionals. This release introduces several enhancements, bug fixes, and new features to elevate your subdomain probing experience. Subprober facilitates fast and reliable information extraction, making it an invaluable asset for penetration testing workflows.

### Features in V1.0.3:
- Subprober logical bug has resolved .
- Subprober accuracy in results are improved .
- Now Subprober shows the progress of it task .
- Concurrency has been improved .
- Support only stdin .

### Installation

##### Method 1:

```bash
pip install subprober
```

#### Method 2:

```bash
git clone https://github.com/sanjai-AK47/SubProber.git
cd Subprober
pip install .
```

### Help for Subprober:

```yaml
subprober -h
 

   _____       __    ____             __             
  / ___/__  __/ /_  / __ \_________  / /_  ___  _____
  \__ \/ / / / __ \/ /_/ / ___/ __ \/ __ \/ _ \/ ___/
 ___/ / /_/ / /_/ / ____/ /  / /_/ / /_/ /  __/ /    
/____/\__,_/_.___/_/   /_/   \____/_.___/\___/_/     
                                                         
                
                
                    Author : D.Sanjai Kumar @CyberRevoltSecurities

                                                                         
                                                  

          
Subprober - A Fast Probing Tool for Penetration testing

[Description] :

    Subprober is a high-performance tool designed for probing and  extract vital information efficiently.

[Flags]:

    -f, --filename            Specify the filename containing a list of subdomains for targeted probing. 
                              This flag is used to find and analyze status codes and other pertinent details.
                      
    -h, --help                Show this help message for you and exit!
    
    -u, --url                 Specify a target URL for direct probing. This flag allows for the extraction of 
                              status codes and other valuable information.
                      
    -sp. --show-progress      Enable show prgress mode which will show the progress of the Subprober with progress bar like this ( example: |████████████████████████████████████████| 4000/4000 [100%] in 12.4s (3.23/s) ).


    -o, --output              Define the output filename to store the results of the probing operation.

    -c, --concurrency         Set the concurrency level for multiple processes. Default is 10.

    -tl, --title              Retrieve and display the title of subdomains.

    -to, --timeout            Set a custom timeout value for sending requests.

    -sv, --server             Identify and display the server information associated with subdomains.

    -wc, --word-count         Retrieve and display the content length of subdomains.

    -apt, --application-type  Determine and display the application type of subdomains.

    -ex, --exclude            Exclude specific response status code(s) from the analysis.

    -mc, --match              Specify specific response status code(s) to include in the analysis.

    -suo, --save-urls-only    Save only URLs for particular status codes, excluding other information.

    -s, --silent              Enable silent mode to suppress the display of Subprober banner and version information.

    -v, --verbose             Enable verbose mode to display detailed results on the console.

    -cs, --concise            Enable concise mode to display only timeout or request failure URLs or subdomains.

    -exs, --excluded-save     Save the results of excluded status codes when the --exclude switch is enabled.

    -ums, --unmatch-save      Save the results of unmatched status codes when the --match switch is enabled.

    -up, --update             Update Subprober to the latest version through pip.

[INFO]:

    subprober -f subdomains.txt -o output.txt -tl -wc -sv -v -apt -wc -ex 404 500 -suo 200 -v -o output.txt -c 
    
    subprober -u https://example.com -c 20 -to 8  -tl -sv  -wc -apt -ex 404 500 -suo 200 -v -o output.txt
    
    cat subdomains.txt | subprober -c 20 -to 8 -tl -sv -wc -apt -ex 404 500 -suo 200 -v -o output.txt

```

### Usage Examples

#### Basic Usage

```bash
subprober -f subdomains.txt -o output.txt -tl -wc -sv -v -apt -wc -ex 404 500 -suo 200 -v -o output.txt -c
```

### Direct URL Probing

```bash
subprober -u https://example.com -c 20 -to 8 -tl -sv -wc -apt -ex 404 500 -suo 200 -v -o output.txt
```

### Piping Subdomains

```bash
cat subdomains.txt | subprober -c 20 -to 8 -tl -sv -wc -apt -ex 404 500 -suo 200 -v -o output.txt
```

## Flags and Options

### Basic Flags

- **-f, --filename**: Specify the filename containing a list of subdomains for targeted probing.

- **-h, --help**: Show the help message and exit.

- **-u, --url**: Specify a target URL for direct probing.

- **-sp, --show-progress**: Enable show progress mode to display a progress bar.

- **-o, --output**: Define the output filename to store the results.

### Advanced Flags

- **-c, --concurrency**: Set the concurrency level for multiple processes. Default is 10.

- **-tl, --title**: Retrieve and display the title of subdomains.

- **-to, --timeout**: Set a custom timeout value for sending requests.

- **-sv, --server**: Identify and display the server information associated with subdomains.

- **-wc, --word-count**: Retrieve and display the content length of subdomains.

- **-apt, --application-type**: Determine and display the application type of subdomains.

- **-ex, --exclude**: Exclude specific response status code(s) from the analysis.

- **-mc, --match**: Specify specific response status code(s) to include in the analysis.

- **-suo, --save-urls-only**: Save only URLs for particular status codes, excluding other information.

- **-s, --silent**: Enable silent mode to suppress the display of Subprober banner and version information.

- **-v, --verbose**: Enable verbose mode to display detailed results on the console.

- **-cs, --concise**: Enable concise mode to display only timeout or request failure URLs or subdomains.

- **-exs, --excluded-save**: Save the results of excluded status codes when the --exclude switch is enabled.

- **-ums, --unmatch-save**: Save the results of unmatched status codes when the --match switch is enabled.

- **-up, --update**: Update Subprober to the latest version through pip.

### License

Subprober is open-source software licensed under the MIT License. See the [LICENSE](https://github.com/sanjai-AK47/Subprober/blob/main/LICENSE) file for details.

### Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to help improve Subprober.


### Sample Usage of Subprober:
![Screenshot from 2023-11-12 19-00-28](https://github.com/sanjai-AK47/SubProber/assets/119435129/2403d849-c91f-4d09-92f5-8314ae1a18ef)

### Information:
This tool is developed by [D.Sanjai Kumar](https://www.linkedin.com/in/d-sanjai-kumar-109a7227b/) for support the open source community for CyberSecurity and Ethical Hacking and
The Subprober is built for reconnaissance and ethical hacking purposes and developer is not responsible for any unethical purposes so
please use the Subprober with responsible and Ethically . Happy Hacking Hackers you can support my contribution by giving a ⭐ to the Subprober which motivate me to develop more like this ♥️.


