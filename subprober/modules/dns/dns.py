from subprober.modules.logger.logger import logger
from subprober.modules.utils.utils import GetDomain
import aiodns
import asyncio
import socket

async def dns(resolver: aiodns.DNSResolver, url, record_type, args) -> list[str]:
    try:
        domain = GetDomain(url)  
        results = await resolver.query(domain, record_type)
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
        if args.verbose:
            logger(f"Exception occurred in the dns resolver module due to: {e}, {type(e)}", "warn", args.no_color)
        return []