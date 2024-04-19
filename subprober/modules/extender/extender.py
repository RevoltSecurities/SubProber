import resource
import platform

def __extender__():
    try:
        soft , hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        new = 1000000
        osname = platform.system()
        if osname == "Linux" or  osname == "Darwin":
            resource.setrlimit(resource.RLIMIT_NOFILE, (new, hard))
    except KeyboardInterrupt as e:
        quit()
    except Exception as e:
        print(f"At extender: {e}, {type(e)}")