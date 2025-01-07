from subprober.modules.logger.logger import logger
import aiofiles
import asyncio
import json

async def save(filename: str, content: str, Json: bool, nocolor=False) -> None:
    try:
        async with aiofiles.open(filename, "a") as streamw:
            if Json:
                await streamw.write(json.dumps(content, indent=4)+ "\n")
            else:
                await streamw.write(content + '\n')
    except (KeyboardInterrupt,asyncio.CancelledError):
        exit(1)
    except Exception as e:
        logger(f"Excpetion occured in the save module due to: {e}, {type(e)}, {content}", "warn", nocolor)