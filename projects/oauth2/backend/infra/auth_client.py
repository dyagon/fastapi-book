import time
import base64
import asyncio
import httpx

from typing import Optional, Dict, Any

from pydantic import BaseModel

from fastapi_book import BaseInfra


class OAuthClientConfig(BaseModel):
    base_url: str
    token_url: str
    client_id: str
    client_secret: str


# 管理 client credentials 的 token
class M2MTokenManager:

    def __init__(self, token_url, client_id, client_secret):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = asyncio.Lock()

    @property
    def is_expired(self) -> bool:
        """
        判断 token 是否过期，增加 60 秒的缓冲时间
        """
        return time.time() > self._expires_at - 60

    @property
    def basic_auth_header(self) -> str:
        """Create HTTP Basic Auth header for client authentication."""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    async def get_token(self) -> str:
        async with self._lock:
            if self._access_token is None or self.is_expired:
                await self._fetch_new_token()
        return self._access_token

    async def _fetch_new_token(self):
        data = {
            "grant_type": "client_credentials",
            "scope": "get_client_info"
        }
        headers = {
            "Authorization": self.basic_auth_header,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            async with httpx.AsyncClient() as client:
                # Get access token using client credentials
                response = await client.post(self.token_url, data=data, headers=headers)
                response.raise_for_status()
                token_data = response.json()
                self._access_token = token_data["access_token"]
                self._expires_at = time.time() + token_data["expires_in"]
        except httpx.HTTPStatusError as e:
            print(f"Failed to fetch new token: {e.response.text}")
            self._access_token = None
            self._expires_at = 0.0
            raise e
        

class OAuthClient(BaseInfra):

    def __init__(self, config: OAuthClientConfig):
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0
        self._lock = asyncio.Lock()
        self.base_url = config.base_url
        self.token_manager = M2MTokenManager(config.token_url, config.client_id, config.client_secret)

    @property
    async def bearer_auth_header(self) -> str:
        return f"Bearer {await self.token_manager.get_token()}"

    async def get_token(self) -> str:
        return await self.token_manager.get_token()

    async def call(self, endpoint: str):
        url = f"{self.base_url}{endpoint}"

        headers = {"Authorization": await self.bearer_auth_header}

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                return {
                    "error": f"HTTP {e.response.status_code}",
                    "detail": e.response.text,
                }
            except Exception as e:
                return {"error": "Request failed", "detail": str(e)}
