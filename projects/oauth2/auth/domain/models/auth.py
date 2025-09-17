from typing import Optional, Literal
from pydantic import BaseModel, constr, Field



class AuthorizeRequest(BaseModel):
    client_id: str
    redirect_uri: str
    scope: Optional[str] = None
    state: Optional[str] = None
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None # 推荐只支持 S256

    def get_scopes_list(self) -> list[str]:
        """将 scope 字符串转换为列表"""
        return [s.strip() for s in self.scope.split() if s.strip()]
        
    def invalid_scopes(self, scope: list[str]) -> list[str]:
        if not self.scope:
            return []
        return [s for s in self.get_scopes_list() if s not in scope]



class AuthorizeRequestQuery(AuthorizeRequest):
    response_type: constr(pattern=r'^code$') # 强制 response_type 必须为 "code"



class AuthorizeRequestForm(AuthorizeRequest):
    """
    POST /authorize 的请求体模型
    这些数据将由用户在登录页面上的表单中提交
    """
    # 用户凭据
    username: str
    password: str
    
    # 授权决定
    consent: bool = Field(..., description="用户是否同意授权")


class AuthorizationCodeResponse(BaseModel):
    code: str
    state: Optional[str] = None
    scope: Optional[str] = None

