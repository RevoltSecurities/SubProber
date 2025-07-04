import platform
import resource

def extender():  
    try:
        soft , hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        new = 100000
        osname = platform.system()
        if osname == "Linux" or  osname == "Darwin":
            resource.setrlimit(resource.RLIMIT_NOFILE, (new, hard))
    except KeyboardInterrupt as e:
        exit(1)
    except Exception as e:
        pass