# SubProber (Docker Edition)
Subprober is a powerful and efficient subdomain scanning tool written in Python. With the ability to handle large lists of subdomains. The tool offers concurrent scanning, allowing users to define their preferred concurrency level for faster results. Whether you are on Linux, Windows, or Mac OS.

![image](https://github.com/user-attachments/assets/5075acc2-d164-4e54-94f4-8633170319fe)

---

## Docker Installation

### 1. Clone the Repository
```bash
git clone https://github.com/revoltsecurity/SubProber.git
cd SubProber
```

### 2. Build the Docker Image
```bash
sudo docker build -t subprober .
```

---

## Usage via Docker

### Available Flags

SubProber has a **wide array of probing, filtering, and output options**. For a full list of flags, run:

```bash
sudo docker run --rm --init subprober --help
```

---

### Example Docker Run

```bash
docker run --rm \
  -v $(pwd)/input.txt:/input.txt \
  -v $(pwd)/results:/output \
  subprober -f /input.txt -ip -tl -wc -o /output/subprober.txt
```

> This will:
> 
> - Use `input.txt` from the current directory
>     
> - Save results to `results/subprober.txt`
>     
> - Run probes for IP address, page title, and word count
>     

## Example Use Cases
### 1. Basic IP + Title Probe
```bash
sudo docker run --rm -v $(pwd)/subs.txt:/input.txt subprober -f /input.txt -ip -tl
```
### 2. Match Specific HTTP Status Codes (200, 403)
```bash
sudo docker run --rm -v $(pwd)/subs.txt:/input.txt subprober -f /input.txt -mc 200,403
```
### 3. Take Screenshots and Save to Folder
```bash
sudo docker run --rm -v $(pwd)/subs.txt:/input.txt -v $(pwd)/screenshots:/screenshots subprober -f /input.txt -ss -sp /screenshots
```
### 4. JSON Output with Redirect Info
```bash
sudo docker run --rm -v $(pwd)/subs.txt:/input.txt -v $(pwd)/results:/output subprober -f /input.txt -J -ar -rdu -o /output/output.json
```
---
## Clean Up
To stop and remove all SubProber containers:
```bash
docker ps -q --filter ancestor=subprober | xargs -r docker stop
```
---
## Troubleshooting
- **Tool hangs in Docker?** This can happen due to unclean asyncio exit — use `Ctrl+C` to terminate if needed.
- **Permissions issue?** Ensure your input/output paths are accessible to Docker (especially when using `sudo`).
- **Want to test inside container?**
```bash
docker run -it --entrypoint /bin/bash subprober
```

---

## Maintainer
Developed and maintained by [RevoltSecurities](https://github.com/RevoltSecurities)
