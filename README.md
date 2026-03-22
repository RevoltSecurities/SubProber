<h1 align="center">Subprober</h1>

<p align="center">
  An essential HTTP multi-purpose Probing Tool for Penetration Testers and Security Researchers
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/RevoltSecurities/Subprober" alt="Last Commit">
  <img src="https://img.shields.io/github/v/release/RevoltSecurities/Subprober" alt="Release">
  <a href="https://github.com/RevoltSecurities/Subprober/blob/main/LICENSE"><img src="https://img.shields.io/github/license/RevoltSecurities/Subprober" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.13%2B-blue" alt="Python">
</p>

<h1 align="center">
  <img src="https://github.com/RevoltSecurities/SubProber/assets/119435129/5b763884-6bb2-4881-9005-2cfc9b3a0d35" width="700px">
</h1>

## Features

- High-performance async HTTP probing with aiohttp
- Go-style bounded worker pool with backpressure for efficient concurrency
- LevelDB-backed host deduplication — handles millions of hosts without memory issues
- Instant stop/resume — CTRL+C saves state in <100ms, resume picks up exactly where you left off
- Headless browser screenshots via Playwright (Chromium)
- JARM fingerprinting, TLS data extraction, WebSocket detection
- Flexible match/filter system (status codes, regex, response time, word count, etc.)
- JSON output with full redirect history, request/response headers
- Custom ports, paths, HTTP methods, headers, proxies, SNI
- CIDR range expansion for network scanning
- Docker support for CI/CD pipelines

## Probing Capabilities

| Probe               | Flag             | Probe                  | Flag             |
|----------------------|------------------|------------------------|------------------|
| Status Code          | `-status-code`   | Response Time          | `-rpt`           |
| Title                | `-title`         | Word Count             | `-wc`            |
| Server               | `-server`        | Line Count             | `-lc`            |
| Content Length        | `-cl`            | Content Type           | `-application-type` |
| Redirect Location    | `-location`      | HTTP Version           | `-htv`           |
| IP Address           | `-ip`            | HTTP Reason            | `-hrs`           |
| CNAME                | `-cname`         | JARM Fingerprint       | `-jarm`          |
| AAAA Records         | `-aaaa`          | WebSocket              | `-wss`           |
| TLS Data             | `-tls`           | Body Hash (md5/sha256/mmh3/simhash) | `-hash` |
| Body Preview         | `-bp`            | HTTP Method            | `-dmt`           |

---

## Installation

### Requirements

- **Python 3.13+**
- **LevelDB** C library (required by `plyvel`)

### Install LevelDB (system dependency)

<details>
<summary><b>macOS</b></summary>

```bash
brew install leveldb
```

</details>

<details>
<summary><b>Ubuntu / Debian</b></summary>

```bash
sudo apt-get update
sudo apt-get install -y libleveldb-dev
```

</details>

<details>
<summary><b>Fedora / RHEL / CentOS</b></summary>

```bash
sudo dnf install -y leveldb-devel
```

</details>

<details>
<summary><b>Arch Linux</b></summary>

```bash
sudo pacman -S leveldb
```

</details>

<details>
<summary><b>Alpine Linux</b></summary>

```bash
apk add leveldb-dev
```

</details>

<details>
<summary><b>Windows</b></summary>

On Windows, install via [vcpkg](https://github.com/microsoft/vcpkg):

```powershell
vcpkg install leveldb
```

Or use WSL2 with an Ubuntu installation and follow the Ubuntu instructions above.

</details>

### Install Subprober

**Using uv (Recommended):**

```bash
uv tool install git+https://github.com/RevoltSecurities/Subprober.git
subprober -h
```

**Using pipx:**

```bash
pipx install git+https://github.com/RevoltSecurities/Subprober.git
subprober -h
```

**Using pip:**

```bash
pip install git+https://github.com/RevoltSecurities/Subprober.git
subprober -h
```

**From source:**

```bash
git clone https://github.com/RevoltSecurities/Subprober.git
cd Subprober
pip install .
subprober -h
```

> **Note (macOS Apple Silicon):** If `plyvel` fails to build with `symbol not found '__ZTIN7leveldb10ComparatorE'`, rebuild it with RTTI disabled:
> ```bash
> CXXFLAGS="-I$(brew --prefix leveldb)/include -fno-rtti" \
> LDFLAGS="-L$(brew --prefix leveldb)/lib -Wl,-rpath,$(brew --prefix leveldb)/lib" \
> pip install --force-reinstall --no-cache-dir --no-build-isolation plyvel
> ```

### Install Playwright (for screenshots)

```bash
playwright install chromium
```

---

## Docker

### Build

```bash
docker build -t subprober .
```

### Run

```bash
# Basic probing
echo "example.com" | docker run -i subprober -status-code -title -server

# From a host list (mount as volume)
docker run -i -v $(pwd):/data subprober -l /data/hosts.txt -status-code -title -o /data/results.txt

# JSON output
cat hosts.txt | docker run -i subprober -status-code -title -server -json

# With screenshots (mount output directory)
docker run -i -v $(pwd):/data subprober -l /data/hosts.txt -ss -sp /data/screenshots -status-code -title

# Use -stats flag for Docker (no interactive progress bar)
cat hosts.txt | docker run -i subprober -status-code -title -stats
```

### Docker Compose

```yaml
services:
  subprober:
    build: .
    volumes:
      - ./data:/data
    command: ["-l", "/data/hosts.txt", "-status-code", "-title", "-o", "/data/results.txt", "-stats"]
```

---

## Usage

### Basic Examples

```bash
# Probe a single URL
subprober -u example.com -status-code -title -server

# Probe from a file
subprober -l hosts.txt -status-code -title

# Pipe from other tools (e.g., subfinder)
subfinder -d example.com -silent | subprober -status-code -title -server

# JSON output with all data
subprober -l hosts.txt -status-code -title -server -json -fo -o results.json

# Custom ports and paths
subprober -l hosts.txt -port 8080,8443 -path /api,/admin -status-code -title

# With screenshots
subprober -l hosts.txt -status-code -title -ss -sp ./screenshots

# Filter/match responses
subprober -l hosts.txt -status-code -title -mc 200,301 -fc 404,500
```

### Stop and Resume

Subprober supports instant stop/resume for large scans. On CTRL+C, the current state is saved to a lightweight resume file in under 100ms — no matter how many hosts remain.

```bash
# Start a large scan
subprober -l million_hosts.txt -status-code -title -c 200

# Press CTRL+C at any time — generates resume_XXXXXXXX.cfg
# Resume exactly where you left off
subprober -resume resume_XXXXXXXX.cfg -status-code -title -c 200

# Chain multiple resumes — each saves only the remaining hosts
```

### All Options

```
INPUT:
  -l,  --list              specify a file containing a list of URLs to probe
  -u,  --url               specify URL(s) to probe (comma-separated)
  -resume, --resume        resume a previous scan from a .cfg file
  stdin/stdout             pipe input from other tools

PROBES:
  -status-code             display status code
  -title                   display page title
  -server                  display server header
  -wc                      display word count
  -lc                      display line count
  -cl                      display content length
  -location                display redirect location
  -application-type        display content type
  -ip                      display IP address
  -cname                   display CNAME records
  -aaaa                    display AAAA records
  -htv                     display HTTP version
  -hrs                     display HTTP reason
  -jarm                    display JARM fingerprint
  -rpt                     display response time
  -wss                     display WebSocket support
  -hash                    display body hash (md5,mmh3,simhash,sha1,sha256,sha512)
  -dmt                     display HTTP method
  -bp                      display body preview (default: 100 chars)
  -body                    POST body to include in request
  -resolvers               custom DNS resolvers (comma-separated or file)

CONFIG:
  -dhp                     disable HTTP fallback (HTTPS only)
  -X,  --method            HTTP method (get,post,head,put,delete,patch,trace,connect,options)
  -H,  --header            custom headers (repeatable)
  -ra                      enable random User-Agent
  -proxy                   HTTP/SOCKS proxy URL
  -ar                      follow redirects
  -maxr                    max redirects (default: 10)
  -sni                     custom TLS SNI hostname
  -stats                   show stats instead of progress bar (for Docker/CI)

MISCELLANEOUS:
  -path                    path(s) to append (file or comma-separated)
  -port                    custom port(s) (file or comma-separated)
  -tls                     extract TLS certificate data

HEADLESS:
  -ss                      take screenshots (requires Playwright)
  -st                      screenshot timeout (default: 15s)
  -scp                     system Chrome path
  -pdf                     save as PDF instead of PNG
  -no-fpg                  disable full-page screenshot
  -icb                     include screenshot bytes in JSON output
  -hos                     additional Chrome options
  -sid                     idle time before screenshot (default: 1s)
  -sp                      screenshot output directory

MATCHERS:
  -mc                      match by status codes (200,302)
  -mcr                     match by status code range (200-299)
  -ms                      match by response string
  -mr                      match by regex
  -mpt                     match by URL path
  -ml                      match by response length
  -mlc                     match by line count
  -mwc                     match by word count
  -mrt                     match by min response time

FILTERS:
  -fc                      filter by status codes (404,500)
  -fcr                     filter by status code range (400-499)
  -fs                      filter by response string
  -fr                      filter by regex
  -fpt                     filter by URL path
  -fl                      filter by response length
  -flc                     filter by line count
  -fwc                     filter by word count
  -frt                     filter by max response time

OUTPUT:
  -o,  --output            output file path
  -json                    JSON output format
  -rdu                     include redirect URLs (requires -json -ar)
  -rdh                     include redirect history (requires -json -ar)
  -rsc                     include redirect status codes (requires -json -ar)
  -rqh                     include request headers (requires -json -ar)
  -rsh                     include response headers (requires -json -ar)
  -fo                      include all available data (requires -json)

RATE-LIMIT:
  -c,  --concurrency       concurrency level (default: 100)
  -rtl                     max requests per second (default: 1000)

OPTIMIZATION:
  -timeout                 request timeout in seconds
  -delay                   delay between requests
  -rts                     retry count on failure (default: 0)

DEBUG:
  -silent                  suppress banner output
  -verbose                 show error details
  -nc                      disable colored output
  -debug                   debug mode
```

---

## Architecture

Subprober v3 is built on a Go-inspired architecture:

- **Worker Pool** — Fixed N long-lived worker coroutines pull from a bounded queue. Backpressure prevents memory blowup on large inputs.
- **Fan-Out Producers** — Multiple producer coroutines expand hosts into URLs concurrently, feeding the shared worker queue.
- **LevelDB Disk Cache (HMap)** — Hosts are stored in LevelDB for O(1) deduplication. Supports millions of hosts without touching RAM.
- **Instant Resume** — On interrupt, a lightweight JSON marker points to the persisted LevelDB directory. Resume opens the existing DB in <1 second.
- **Composition-Based HTTP Client** — `RetryableHttp` wraps aiohttp with automatic retry, HTTP fallback, TLS extraction, and response timing.

---

## About

**Subprober** is developed by [RevoltSecurities](https://github.com/RevoltSecurities) to empower security researchers and penetration testers. Designed for efficiency and scale, it streamlines HTTP reconnaissance in modern security workflows.

Released under the [MIT License](LICENSE).
