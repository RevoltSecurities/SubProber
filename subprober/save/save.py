import aiofiles
import json
from subprober.logger.logger import Logger
from typing import Any


class Save():
    def __init__(self, filename:str = None, jsonize: bool = False):
        self.filename = filename
        self.jsonize = jsonize
        self.logger = Logger()
        
    
    async def save(self,content: Any) -> None:
        try:
            if self.filename is None:
                return
            
            async with aiofiles.open(self.filename, "a") as streamw:
                if self.jsonize:
                    await streamw.write(json.dumps(content, indent=4)+ "\n")
                else:
                    await streamw.write(content + '\n')
        except Exception as e:
            self.logger.warn(f"error occured in save module due to: {e}, {type(e)}, {content}")