import aiodns
import asyncio
import socket
import argparse
from subprober.logger.logger import Logger
from subprober.utils.utils import Utils



class AsyncDns:
    def __init__(self, args: argparse.Namespace, nameservers=None):
        self.logger = Logger()
        self.utils = Utils()
        self.args = args
        self.nameservers = nameservers if nameservers else ["1.1.1.1", "8.8.8.8"]
        try:
            self.loop = asyncio.get_event_loop()
            self.resolver = aiodns.DNSResolver(loop=self.loop, nameservers=self.nameservers, rotate=True)
        except Exception as e:
            self.logger.warn(f"Failed to initialize DNS resolver: {e}, {type(e)}")
            self.resolver = None

    async def resolve(self, url: str, record_type: str) -> list[str]:
        if not self.resolver:
            return []

        try:
            domain = self.utils.GetDomain(url)
            if not domain:
                return []

            results = await self.resolver.query(domain, record_type)
            await asyncio.sleep(0)  
            if record_type == 'CNAME':
                return [results.cname] if hasattr(results, 'cname') else []
            elif record_type in ('A', 'AAAA'):
                return [result.host for result in results] if results else []
            else:
                return []

        except (KeyboardInterrupt, asyncio.CancelledError):
            return []
        except (socket.gaierror, aiodns.error.DNSError, TimeoutError):
            return []
        except Exception as e:
            if self.args.verbose:
                self.logger.warn(f"Exception occurred in the DNS resolver module due to: {e}, {type(e)}")
            return []
