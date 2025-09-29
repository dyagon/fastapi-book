from fastapi import Request, status

from fastapi.responses import JSONResponse
from ..domain.exception import OAuth2Exception, OAuth2ErrorCode


OAuth2ErrorCodeMap = {
    OAuth2ErrorCode.INVALID_REQUEST: status.HTTP_400_BAD_REQUEST,
    OAuth2ErrorCode.UNAUTHORIZED_CLIENT: status.HTTP_401_UNAUTHORIZED,
    OAuth2ErrorCode.ACCESS_DENIED: status.HTTP_403_FORBIDDEN,
    OAuth2ErrorCode.UNSUPPORTED_RESPONSE_TYPE: status.HTTP_400_BAD_REQUEST,
    OAuth2ErrorCode.INVALID_SCOPE: status.HTTP_400_BAD_REQUEST,
    OAuth2ErrorCode.SERVER_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    OAuth2ErrorCode.TEMPORARILY_UNAVAILABLE: status.HTTP_503_SERVICE_UNAVAILABLE,
    OAuth2ErrorCode.INVALID_GRANT: status.HTTP_400_BAD_REQUEST,
    OAuth2ErrorCode.UNSUPPORTED_GRANT_TYPE: status.HTTP_400_BAD_REQUEST,
}



async def oauth2_exception_handler(request: Request, exc: OAuth2Exception):
    print(exc)
    return JSONResponse(
        status_code=OAuth2ErrorCodeMap[exc.error],
        content={"error": exc.error, "error_description": exc.error_description},
    )