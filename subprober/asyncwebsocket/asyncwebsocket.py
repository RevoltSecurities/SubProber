import websockets
import websockets.connection
import asyncio
from subprober.logger.logger import Logger
import argparse

class AsyncWebsocket:
    def __init__(self, args: argparse.Namespace):
        self.logger = Logger()
        self.args = args

    async def asyncconnect(self, url: str) -> str:
        wsurl = ""
        if url.startswith("https://"):
            wsurl = url.replace("https://", "wss://", 1)
        elif url.startswith("http://"):
            wsurl = url.replace("http://", "ws://", 1)
        else:
            if self.args.verbose:
                self.logger.warn(f"Warning: URL '{url}' has no http/https scheme, cannot convert to ws/wss.")
            return "disallowed"
        try:
            async with websockets.connect(wsurl, open_timeout=5) as socket:
                return "allowed"
        except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
        except websockets.exceptions.InvalidStatusCode:
            return "disallowed"
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occurred in the WebSocketProber for {url} due to: {e}, {type(e)}")
            return "disallowed"