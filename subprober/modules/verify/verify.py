import importlib.metadata as data
def __getverify__(pkg):
    version = data.version(pkg)
    return version