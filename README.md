# Subprober - Subdomain HTTP Status Code Checker

Subprober is a Python tool designed to efficiently check the HTTP status codes of a list of subdomains. It uses concurrent features to speed up the process, and users can define their preferred concurrency level to optimize the scanning speed. Additionally, Subprober provides a Linux binary file that can be easily executed from any terminal by placing it in the `/usr/local/bin` directory. For Windows and macOS users, they can run the `subprober.py` file directly.

## Features

- Check HTTP status codes of multiple subdomains in parallel.
- Customizable concurrency level for faster scanning.
- Cross-platform support with Linux binary and Python script for Windows and macOS.
- Verbose mode to print detailed output.
- Option to save the output to a file.

## Requirements

- Python 3.x

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/sanjai-AK47/Subprober.git
   ```

2. Change to the Subprober directory:

   ```bash
   cd Subprober
   ```

3. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. If you are using Linux, you can use the pre-built binary file `subprober`:

   ```bash
   sudo cp subprober /usr/local/bin
   ```

   For Windows and macOS, run the Python script:

   ```bash
   python subprober.py
   ```

## Usage

Run Subprober from the command line with the following options:

```bash
Usage: subprober [OPTIONS]

Options:
  -f, --filename TEXT        File containing the list of subdomains to check
  -c, --concurrency INTEGER  Number of concurrent requests (default: 10)
  -v, --verbose              Print verbose output
  -o, --output TEXT          Save the output to a file
  --help                     Show this message and exit.
```

- `-f` or `--filename`: Specify the file containing the list of subdomains to check.

- `-c` or `--concurrency`: Set the concurrency level. Higher values increase scanning speed, but use it cautiously to avoid overloading the target server.

- `-v` or `--verbose`: Print detailed output while scanning.

- `-o` or `--output`: Save the output to a file.

## Examples

1. Check status codes for a list of subdomains in `subdomains.txt` with 20 concurrent requests and save the output to `results.txt`:

   ```bash
   subprober -f subdomains.txt -c 20 -o results.txt
   ```

2. Use the default concurrency level (10) to check status codes and print verbose output:

   ```bash
   subprober -f subdomains.txt -v
   ```

## Report Iussues

1.If any user facing any issues when running the subprober python file or Issue with the Linux binary file can report their issues

2.For you each feedbacks the Subprober will getting upgraded with more features

# Thank You

