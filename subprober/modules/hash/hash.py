import hashlib
import mmh3
from simhash import Simhash
from subprober.modules.logger.logger import logger
import asyncio

def tokenize_for_simhash(text: str) -> list[str]:
    return text.lower().split() 

async def Hashgen(response: str, algorithms: list[str], args) -> dict[str]:
    try:
        response = response.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
        hashed = {}

        for alg in algorithms:
            try:
                algo = alg.strip().lower()
                if algo == "md5":
                    hashed[algo] = hashlib.md5(response.encode("utf-8")).hexdigest()
                elif algo == "sha1":
                    hashed[algo] = hashlib.sha1(response.encode("utf-8")).hexdigest()
                elif algo == "sha256":
                    hashed[algo] = hashlib.sha256(response.encode("utf-8")).hexdigest()
                elif algo == "sha512":
                    hashed[algo] = hashlib.sha512(response.encode("utf-8")).hexdigest()
                elif algo == "mmh3":
                    hashed[algo] = str(mmh3.hash(response.encode("utf-8")))
                elif algo == "simhash":
                    tokens = tokenize_for_simhash(response)
                    hashed[algo] = str(Simhash(tokens).value)
                else:
                    if args.verbose:
                        logger(f"Undefined hash algorithm: {algo}", "error", args.no_color)
            except Exception as inner_e:
                logger(
                    f"Error with algorithm '{algo}': {inner_e}, {type(inner_e)}",
                    "error",
                    args.no_color,
                )
    except (KeyboardInterrupt, asyncio.CancelledError):
        exit(1)
    except Exception as e:
        if args.verbose:
            logger(f"Exception occurred in Hashgen: {e}, {type(e)} {algo}", "warn", args.no_color)
    finally:
        return hashed
