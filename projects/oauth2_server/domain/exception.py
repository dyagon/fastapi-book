from typing import Optional

from enum import StrEnum 

class OAuth2ErrorCode(StrEnum):
    """
    符合 RFC 6749 和相关规范的 OAuth2 错误码枚举。
    """
    # --- RFC 6749, Section 5.2 ---
    #: 请求缺少必需参数、包含不支持的参数值、参数重复或格式错误。
    INVALID_REQUEST = "invalid_request"
    
    #: 客户端未被授权使用此授权类型，或客户端认证失败。
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    
    #: 资源所有者（用户）或授权服务器拒绝了请求。
    ACCESS_DENIED = "access_denied"
    
    #: 授权服务器不支持 `response_type` 参数指定的值。
    UNSUPPORTED_RESPONSE_TYPE = "unsupported_response_type"
    
    #: 请求的 scope 无效、未知、格式不正确，或超出了客户端被允许的范围。
    INVALID_SCOPE = "invalid_scope"
    
    #: 服务器遇到意外情况，无法完成请求。
    SERVER_ERROR = "server_error"
    
    #: 由于临时过载或维护，服务器当前无法处理请求。
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"

    # --- RFC 6749, Section 4.1.2.1 & 4.2.2.1 ---
    
    #: 提供的授权凭证（如授权码、刷新令牌）无效、过期或已被撤销。
    INVALID_GRANT = "invalid_grant"
    #: 授权服务器不支持该授权类型 (`grant_type`)。
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"



class OAuth2Exception(Exception):
    """
    OAuth2 领域异常的基类。
    它只包含 OAuth2 相关的错误信息，与 HTTP 完全解耦。
    """
    def __init__(
        self,
        error: OAuth2ErrorCode, # 持有整个枚举成员
        error_description: str,
        error_uri: Optional[str] = None,
    ):
        self.error = error
        self.error_description = error_description
        self.error_uri = error_uri
        super().__init__(f"[{self.error.name}] {error_description}")


class InvalidRequestException(OAuth2Exception):
    def __init__(
        self,
        error_description: str = "The request is missing a required parameter, includes an invalid parameter value, or is otherwise malformed.",
    ):
        super().__init__(
            error=OAuth2ErrorCode.INVALID_REQUEST,
            error_description=error_description,
        )


class UnauthorizedClientException(OAuth2Exception):
    def __init__(self, error_description: str = "Client authentication failed."):
        super().__init__(
            error=OAuth2ErrorCode.UNAUTHORIZED_CLIENT, # 只需传递枚举成员
            error_description=error_description
        )


class InvalidGrantException(OAuth2Exception):
    def __init__(self, error_description: str = "The provided authorization grant is invalid, expired, or revoked."):
        super().__init__(
            error=OAuth2ErrorCode.INVALID_GRANT,
            error_description=error_description
        )


class UnsupportedGrantTypeException(OAuth2Exception):
    def __init__(
        self,
        error_description: str = "The authorization grant type is not supported by the authorization server.",
    ):
        super().__init__(
            error=OAuth2ErrorCode.UNSUPPORTED_GRANT_TYPE,
            error_description=error_description,
        )
