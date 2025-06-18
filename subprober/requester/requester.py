import httpx
import asyncio
import argparse
from subprober.logger.logger import Logger 
from subprober.utils.utils import Utils   

class Requester:
    def __init__(self, args: argparse.Namespace): 
        self.args = args
        self.logger = Logger() 
        self.utils = Utils()  
                              
    async def request(
        self,
        method: str,
        url: str,
        client: httpx.AsyncClient,
        data: dict | None = None,
        json: dict | None = None,
        content: bytes | str | None = None,
        auth: httpx.Auth | tuple | None = None,       
        cookies: dict | httpx.Cookies | None = None,  
    ) -> httpx.Response | None:
        try: 
            headers = {}
            
            if self.args.header:
                for header_str in self.args.header:
                    try:
                        name, value = header_str.split(':', 1)
                        headers[name.strip()] = value.strip()
                    except ValueError:
                        self.logger.warn(f"Invalid header format: '{header_str}'. Expected 'Name:Value'.", self.args.no_color)

            headers["User-Agent"] = self.utils.Useragents() if self.args.random_agent else "git+Subprober/V2"

            extensions = None
            if self.args.sni_hostname:
                extensions = {"sni_hostname": self.args.sni_hostname} 

            response = await client.request(
                method.upper(),
                url,
                headers=headers,
                data=data,        
                json=json,        
                content=content,  
                timeout=self.args.timeout,  
                auth=auth,        
                cookies=cookies,  
                follow_redirects=self.args.allow_redirect,
                extensions=extensions
            )
            return response
        
        except (httpx.ConnectError, httpx.ConnectTimeout) as e:
            if self.args.verbose:
                self.logger.debug(f"Connection error/timeout for {url} ({method}): {e}", self.args.no_color)
            return None
        except (KeyboardInterrupt, asyncio.CancelledError):
            exit(1)
        except Exception as e:
            if self.args.verbose:
                self.logger.error(f"Exception occurred in Requester.request for {url} ({method}) due to: {e}, {type(e)}", self.args.no_color)
            return None