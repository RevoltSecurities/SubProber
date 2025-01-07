import requests
from rich.console import Console
from rich.markdown import Markdown
from subprober.modules.logger.logger import logger

console = Console()

def updatelog():
    try:
        url = f"https://raw.githubusercontent.com/RevoltSecurities/SubProber/main/subprober/updatelog.md"
        response = requests.get(url, timeout=20, stream=True)
        if response.status_code == 200:
            loader = response.text
            console.print(Markdown(loader))
        else:
            logger("Unable to get the new updates of the subprober, please try to vist here: https://github.com/RevoltSecurities/SubProber/blob/main/subprober/updatelog.md", "info")
            quit()
    except Exception as e:
        pass