# exceptions.py
class SessionException(Exception):
    def __init__(self, detail: str = "Session Error"):
        self.detail = detail
        super().__init__(self.detail)


class NotAuthenticatedException(SessionException):
    def __init__(self, detail: str = "User is not authenticated."):
        super().__init__(detail)

class PermissionDeniedException(SessionException):
    """
    当用户已认证但没有执行操作的权限时引发。
    通常映射到 HTTP 403 Forbidden。
    """
    def __init__(self, detail: str = "User does not have enough permissions."):
        super().__init__(detail)

class SessionExpiredException(SessionException):
    """
    当用户的会话已过期时引发。
    通常映射到 HTTP 401 Unauthorized，并可能带有一个特定的错误代码或消息。
    """
    def __init__(self, detail: str = "Session has expired, please log in again."):
        super().__init__(detail)

class InvalidCredentialsException(SessionException):
    """
    在登录过程中，当提供的用户名或密码不正确时引发。
    通常映射到 HTTP 401 Unauthorized。
    """
    def __init__(self, detail: str = "Invalid username or password."):
        super().__init__(detail)

class MissingSessionTokenException(SessionException):
    """
    当请求中缺少必要的 session token 时引发。
    通常映射到 HTTP 401 Unauthorized。
    """
    def __init__(self, detail: str = "Session token is missing from the request."):
        super().__init__(detail)

