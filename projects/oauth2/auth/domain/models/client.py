from pydantic import BaseModel
from typing import Optional



class Client(BaseModel):
    client_id: str
    client_secret: Optional[str]  # None for public clients
    redirect_uris: list[str]
    scopes: list[str]
    client_type: str  # "confidential" or "public"

    def is_public_client(self) -> bool:
        """检查是否为公共客户端"""
        return self.client_type == "public"

    def check_redirect_uri(self, redirect_uri: str) -> bool:
        """检查重定向 URI 是否在允许的列表中"""
        return redirect_uri in self.redirect_uris

