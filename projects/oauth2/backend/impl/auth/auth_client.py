import httpx


from .auth_strategy import AuthStrategy


import httpx


class AuthClient:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client
        self._auth = auth_strategy

    async def _send_request(self, method: str, url: str, **kwargs):
        """内部方法，用于准备并发送请求。"""
        auth_headers = await self._auth.get_auth_headers()

        user_headers = kwargs.get("headers", {})
        kwargs["headers"] = {**user_headers, **auth_headers}

        client_method = getattr(self._client, method)

        return await client_method(url, **kwargs)

    async def get(self, url, **kwargs):
        return await self._send_request("get", url, **kwargs)

    async def post(self, url, **kwargs):
        return await self._send_request("post", url, **kwargs)

    async def put(self, url, **kwargs):
        return await self._send_request("put", url, **kwargs)

    async def delete(self, url, **kwargs):
        return await self._send_request("delete", url, **kwargs)


# class AuthClient(WebClient):
#     def __init__(self, config: OAuthClientConfig):
#         self.base_url = config.base_url
#         self.token_url = config.token_url
#         self._client_id = config.client_id
#         self._client_secret = config.client_secret

#     @property
#     def basic_auth_header(self) -> str:
#         credentials = f"{self._client_id}:{self._client_secret}"
#         encoded_credentials = base64.b64encode(credentials.encode()).decode()
#         return f"Basic {encoded_credentials}"


# class AuthCodeClient(OAuthClient):
#     def __init__(self, config: AuthorizationCodeClientConfig):
#         super().__init__(config)
#         self.provider = config.provider
#         self._auth_url = config.auth_url
#         self._redirect_uri = config.redirect_uri
#         self._scope = config.scope

#     def make_auth_url(self, state: Optional[str] = None):
#         auth_params = {
#             "response_type": "code",
#             "client_id": self._client_id,
#             "redirect_uri": self._redirect_uri,
#             "scope": self._scope,
#         }
#         if state:
#             auth_params["state"] = state
#         return f"{self._auth_url}?{urlencode(auth_params)}"

#     async def exchange_code_for_tokens(self, code: str):
#         data = {
#             "grant_type": "authorization_code",
#             "code": code,
#             "redirect_uri": self._redirect_uri,
#         }
#         headers = {
#             "Authorization": self.basic_auth_header,
#             "Content-Type": "application/x-www-form-urlencoded",
#         }

#         response = await self._client.post(self.token_url, data=data, headers=headers)
#         response.raise_for_status()
#         return response.json()

#     async def refresh_token(self, refresh_token: str):
#         data = {
#             "grant_type": "refresh_token",
#             "refresh_token": refresh_token,
#             "client_id": self._client_id,
#         }
#         headers = {
#             "Authorization": self.basic_auth_header,
#             "Content-Type": "application/x-www-form-urlencoded",
#         }
#         response = await self._client.post(self.token_url, data=data, headers=headers)
#         response.raise_for_status()
#         return response.json()

#     async def get_user_info(self, access_token: str) -> UserInfoDto:
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#         }
#         user_info_url = f"{self.base_url}/user/info"
#         response = await self._client.get(user_info_url, headers=headers)
#         response.raise_for_status()
#         return UserInfoDto(**response.json())
