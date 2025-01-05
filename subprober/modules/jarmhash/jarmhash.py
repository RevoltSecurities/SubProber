import aiojarm
from subprober.modules.logger.logger import logger
from subprober.modules.utils.utils import GetDomain
import asyncio

async def jarmhash(url, args,port=443) -> str:
    try:
        domain = GetDomain(url)
        result = await aiojarm.scan(domain, port)
        return result[3]
    except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
    except Exception as e:
        logger(f"Excepiton occured in jarm fingerprint generate module due to: {e}, {type(e)}", "warn", args.no_color)