import websockets
import websockets.connection
from subprober.modules.logger.logger import logger
import asyncio

async def AsyncWebsocket(url, args) -> str:
    try:
        if url.startswith("https://"):
            wsurl =  url.replace("https://", "wss://", 1)
        elif url.startswith("http://"):
            wsurl =  url.replace("http://", "ws://", 1)
            
        async with websockets.connect(wsurl) as socket:
            return "allowed"
    except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
    except websockets.exceptions.InvalidStatusCode:
        return "disallowed"
    except Exception as e:
        if args.verbose:
            logger(f"Exception occured in the async websocket module due to: {e}, {type(e)}", "warn", args.no_color)
        return "disallowed"