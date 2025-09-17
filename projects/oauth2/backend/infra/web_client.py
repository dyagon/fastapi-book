import httpx
from starlette.background import P
from fastapi_book import BaseInfra





class WebClient(BaseInfra):
    def __init__(self):
        self._client: httpx.AsyncClient = None

    async def setup(self):
        self._client = httpx.AsyncClient()

    async def shutdown(self):
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        return self._client