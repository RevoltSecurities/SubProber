import httpx
from typing import Optional, Dict, Any

class AsyncClientz:
    def __init__(
        self,
        disable_http_fallback: bool = False,
        retries: int = 0,
        **client_kwargs: Any
    ):
        self.disable_http_fallback = disable_http_fallback
        self._client_kwargs = client_kwargs
        self._retries = retries
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        await self._init_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _init_client(self):
        if self.client is None:
            if self._retries > 0:
                transport = httpx.AsyncHTTPTransport(retries=self._retries)
            else:
                transport = None
            self.client = httpx.AsyncClient(transport=transport, **self._client_kwargs)

    async def request(
        self,
        method: str,
        url: str,
        **kwargs: Any
    ) -> Dict[str, Optional[httpx.Response]]:
        await self._init_client()

        responses_map: Dict[str, Optional[httpx.Response]] = {}

        if url.startswith("https://"):
            https_url = url
            try:
                responses_map[https_url] = await self.client.request(method.upper(), url, **kwargs)
            except Exception as e:
                if self.disable_http_fallback:
                    raise e
                responses_map[https_url] = None

            if not self.disable_http_fallback:
                http_url = url.replace("https://", "http://", 1)
                try:
                    responses_map[http_url] = await self.client.request(method.upper(), http_url, **kwargs)
                except Exception as e:
                    responses_map[http_url] = None
        elif url.startswith("http://"):
            http_url = url
            try:
                responses_map[http_url] = await self.client.request(method.upper(), url, **kwargs)
            except Exception as e:
                raise  e
        else:
            raise ProtocolError(url)
        return responses_map

    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None

    async def init(self):
        await self._init_client()

class ProtocolError(ValueError):
    def __init__(self, url: str):
        super().__init__(f"URL must start with 'http://' or 'https://' — got: {url}. "
                         "Please provide a valid HTTP or HTTPS scheme.")
