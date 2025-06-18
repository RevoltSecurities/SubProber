from subprober.logger.logger import Logger
from subprober.utils.utils import Utils
import aiodns
import asyncio
import socket
import argparse

class AsyncDns:
    def __init__(self,resolver: aiodns.DNSResolver, args: argparse.Namespace):
        self.logger = Logger()
        self.utils = Utils()
        self.resolver = resolver
        self.args = args

    async def resolve(self,url: str, record_type: str) -> list[str]:
        try:
            domain = self.utils.GetDomain(url)
            results = await self.resolver.query(domain, record_type)
            await asyncio.sleep(0.0000001) 
            if record_type == 'CNAME':
                return [results.cname] if hasattr(results, 'cname') else []
            elif record_type == 'A':
                return [result.host for result in results] if results else []
            elif record_type == 'AAAA':
                return [result.host for result in results] if results else []
            else:
                return []
        except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
        except (socket.gaierror, aiodns.error.DNSError, TimeoutError):
            return []
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occurred in the dns resolver module due to: {e}, {type(e)}")
            return []