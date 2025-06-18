import aiojarm
import asyncio
from subprober.logger.logger import Logger
from subprober.utils.utils import Utils
import argparse

class JarmScanner:
    def __init__(self, args: argparse.Namespace):
        self.logger = Logger()
        self.utils = Utils()
        self.args = args

    async def get_jarm_hash(self, url: str, port: int = 443) -> str:
        try:
            domain = self.utils.GetDomain(url)
            result = await aiojarm.scan(domain, port)
            return result[3]
        except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occurred in jarm fingerprint generate module due to: {e}")
            return ""