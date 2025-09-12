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
        
    def invalid_scopes(self, scope: str) -> list[str]:
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



class OAuth2AuthorizationRequest(BaseModel):
    """OAuth2 授权请求参数封装"""
    response_type: str = Field(default="code", description="响应类型")
    client_id: str = Field(..., description="客户端 ID")
    redirect_uri: str = Field(..., description="重定向 URI")
    scope: str = Field(default="get_user_info get_user_role", description="请求的权限范围")
    state: Optional[str] = Field(default=None, description="状态参数")
    code_challenge: Optional[str] = Field(default=None, description="PKCE 代码挑战")
    code_challenge_method: str = Field(default="S256", description="PKCE 代码挑战方法")
    
    class Config:
        # 允许从查询参数创建实例
        extra = "allow"
    
    def get_scopes_list(self) -> list[str]:
        """将 scope 字符串转换为列表"""
        return [s.strip() for s in self.scope.split() if s.strip()]
    
    def has_scope(self, scope: str) -> bool:
        """检查是否包含指定 scope"""
        return scope in self.get_scopes_list()
    
    def is_pkce_required(self) -> bool:
        """检查是否需要 PKCE"""
        return self.code_challenge is not None
    
    def get_redirect_url_with_params(self, **params) -> str:
        """构建带参数的重定向 URL"""
        from urllib.parse import urlencode
        if params:
            return f"{self.redirect_uri}?{urlencode(params)}"
        return self.redirect_uri
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """验证请求参数"""
        # 验证 response_type
        if not OAuth2Defaults.validate_response_type(self.response_type):
            return False, f"不支持的 response_type: {self.response_type}"
        
        # 验证 code_challenge_method
        if not OAuth2Defaults.validate_code_challenge_method(self.code_challenge_method):
            return False, f"不支持的 code_challenge_method: {self.code_challenge_method}"
        
        # 验证 scope
        if not OAuth2Defaults.validate_scope(self.scope):
            return False, f"无效的 scope: {self.scope}"
        
        return True, None
    
    def get_error_redirect_url(self, error: str, error_description: str) -> str:
        """获取错误重定向 URL"""
        params = {
            "error": error,
            "error_description": error_description
        }
        if self.state:
            params["state"] = self.state
        return self.get_redirect_url_with_params(**params)

