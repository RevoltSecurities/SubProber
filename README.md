# Subprober - PyThon based Probing tool for urls and subdomains.

Subprober is a Python tool designed to efficiently probe and get essentials user desired data for list of urls and subdomains subdomains. It uses concurrent features to speed up the process
and users can define their preferred concurrency level to optimize the scanning speed and It probeds and get details for users that they desired by switching the flags for details.Support 
this contribution by giving a ⭐ and show your ♥️!

# Features

- Defaultly get the status codes for urls and subdomains
- Get server name of the web page
- Get title of the  web page 
- Get word count of web page
- Get application type of web page
- Concurrency built-in and user defined values for probing
- Match and Exclude for user desired status codes
- Verbose and concise flags for user desired console system for output
- Update system integrated for future updates
- Supports stdin and stdout to easily pipe to give input for Subprober
- Good colourised CLI interface consolings
- User defined or auto save are integrated
- Asynchronous probing with concurrency integrated
- Probes for http and https protocols for urls and subdomains
- Easy installation through pip

# Requirements

- Subprober requires python 3.11.+

# Installation :

## Method 1:

1. Clone the repository:

```bash
   pip install subprober
   subprober --help
```
If the pip Method installation not worked properly you can also install it thorugh Method 2 below.

## Method 2:

```bash
   git clone https://github.com/sanjai-AK47/Subprober.git
   cd Subprober
   pip install .
   subprober --help
```

## Usage

Run Subprober from the command line with the following options:

```bash
Usage: subprober [OPTIONS]

Options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename FILENAME
                        [INFO]: A filename that contains list of subdomains to probe and find status codes and other informations
  -u URL, --url URL     [INFO]: A url to probe to find status codes and other informations
  -o OUTPUT, --output OUTPUT
                        [INFO]: Filename to write the output
  -c CONCURRENCY, --concurrency CONCURRENCY
                        [INFO]: Concurrency level for Multiple process
  -tl, --title          [INFO]: Get Title of subdomains
  -sv, --server         [INFO]: Get server of subdomains
  -wc, --word-count     [INFO]: Get content length of subdomains
  -apt, --application-type
                        [INFO]: Get application type of subdomains
  -ex [EXCLUDE ...], --exclude [EXCLUDE ...]
                        [INFO]: Exclude the particular response status code
  -mc [MATCH ...], --match [MATCH ...]
                        [INFO]: the particular response status code
  -suo [SAVE_URLS_ONLY ...], --save-urls-only [SAVE_URLS_ONLY ...]
                        [INFO]: Save only urls for particular status codes instead of other informations
  -s, --silent          [INFO]: Switching silent will not print Subprober banner and version
  -v, --verbose         [INFO]: Switching Verbose to console the results
  -cs, --concise        [INFO]: Switching Consice to console time out or request failured urls or subdomains
  -exs, --excluded-save
                        [INFO]: Switching Exluded save the excluded status codes results when --exclude switch is enabled
  -ums, --unmatch-save  [INFO]: Switching Unmatch save the Unmatched status codes results when --match switch is enabled
  -up, --update         [INFO]: Update the Subprober to latest version through pip
                   Show this message and exit.
```

- `-f` or `--filename`: Specify the file containing the list of subdomains to check.
- `-c` or `--concurrency`: Set the concurrency level. Higher values increase scanning speed, but use it cautiously to avoid overloading the target server.
- `-v` or `--verbose`: Print detailed output while scanning.
- `c` or `--concise` : Print the timeout errored urls and subdomains.
- `-s` or `--silent` : Silent swtich doesn't console the banner and version.
- `tl` or `--title`  : Get the Title of the web page that probes.
- `-sv` or `--server` : Get the Server name of the web page that probes.
- `wc` or `--word-coubt` : Get the word count of the web page that probes.
- `apt` or `--application-type`: Get the application type of the web page that probes.
- `mc` or `--match` : The Match flag will help to print and save only user desired status coded results.
- `ums` or `ums` : This flag is used when user uses `-mc` flag to print particular results but when user when users want also save the unmatched urls this flag can be used.
- `-ex` or `--exclude` : Exclude and not console and save the output.
- `-exs` or `--excluded-save` : Swtiching these flags will help to save excluded satus code results when user desired not to print the excluded url but to save the results.
- `-o` or `--output`: Save the output to a file.
- `-up` or `--update`: Update the Subprober to the latest version.

## Run Subprber through flags:

```bash
   subprober -f subdomains.txt -c 20 -o results.txt --verbose --title --server --application-type --word-count -mc 200 301 302
```

###### [INFO]: Subprober prefered concurrency rate is 20 which very efficient to run and get accurate results also avoids rate limiting

## Run Subprober thorugh pipe :
```bash
   subprober --verbose -c 20 -o results.txt --verbose --title --server --application-type --word-count -mc 200 301 302
```

# Sample Image of Subprober:
![Screenshot from 2023-11-12 19-00-28](https://github.com/sanjai-AK47/SubProber/assets/119435129/2403d849-c91f-4d09-92f5-8314ae1a18ef)

## Information:
This tool is developed by [D.Sanjai Kumar](https://www.linkedin.com/in/d-sanjai-kumar-109a7227b/) for support the open source community for CyberSecurity and Ethical Hacking and
The Subprober is built for reconnaissance and ethical hacking purposes and developer is not responsible for any unethical purposes so
please use the Subprober with responsible and Ethically . Happy Hacking Hackers you can support my contribution by giving a ⭐ to the Subprober which motivate me to develop more like this ♥️.


