
from pydantic import BaseModel
from authlib.integrations.httpx_client import AsyncOAuth2Client



class OAuth2ClientCredentialsConfig(BaseModel):
    token_url: str
    client_id: str
    client_secret: str
    scope: str



class OAuth2ClientCredentialsClient:
    def __init__(self, cfg: OAuth2ClientCredentialsConfig):
        self._cfg = cfg
        self._client = AsyncOAuth2Client(
            client_id=cfg.client_id,
            client_secret=cfg.client_secret,
            token_url=cfg.token_url,
            scope=cfg.scope,
        )

    async def get_token(self) -> str:
        return await self._client._fetch_token(grant_type="client_credentials")
    
