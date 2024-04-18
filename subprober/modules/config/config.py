import appdirs
import os
def __getconfig__():
    try:
        dir = appdirs.user_config_dir()
        config = f"{dir}/subprober"
        if not os.path.exists(config):
            os.makedirs(config)
            return config
        return config
    except Exception as e:
        pass