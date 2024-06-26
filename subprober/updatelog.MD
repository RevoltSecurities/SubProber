# Subprober V1.0.9 Update Log

**Whats Changed:**

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
