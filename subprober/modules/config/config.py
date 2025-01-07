import appdirs
import asyncio
import os
def configdir():
    try:
        dir = appdirs.user_config_dir()
        config = f"{dir}/subprober"
        if not os.path.exists(config):
            os.makedirs(config)
            return config
        return config
    except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
    except Exception as e:
        pass