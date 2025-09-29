from fastapi import APIRouter, Depends, HTTPException, Request

from fastapi.security import OAuth2, OAuth2AuthorizationCodeBearer
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from jose import jwt, JWTError
from starlette.status import HTTP_401_UNAUTHORIZED

from ..dto import UserInfoDto
from ...context import AppContainer

router = APIRouter(tags=["Resource"])

class OAuth2ClientCredentialsBearer(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] = None,
        description: str | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            clientCredentials={"tokenUrl": tokenUrl, "scopes": scopes}
        )
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            auto_error=auto_error,
            description=description,
        )

    async def __call__(self, request: Request):
        authorization: str | None = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2ClientCredentialsBearer(tokenUrl="/oauth2/token")


@router.get("/client")
async def get_client_info(
    token: str = Depends(oauth2_scheme),
):
    token_service = AppContainer.token_service()
    return token_service.validate_token(token)


oauth2_auth_code_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/oauth2/authorize", tokenUrl="/oauth2/token"
)


@router.get("/user/info", response_model=UserInfoDto)
async def get_user_info(
    token: str = Depends(oauth2_auth_code_scheme)
):
    token_service = AppContainer.token_service()
    payload = token_service.validate_token(token)
    scopes = payload.get("scope", "")
    if "get_user_info" not in scopes:
        raise HTTPException(status_code=403, detail="Insufficient scope")

    # 检查token类型：authorization code vs client credentials
    user_id = payload.get("sub")
    client_id = payload.get("client_id")

    # 如果sub是用户ID（authorization code流程），获取完整用户信息
    if user_id and user_id != client_id:
        # 通过用户ID获取用户信息
        try:
            user_repo = AppContainer.user_repo()
            user = await user_repo.get_user_by_id(user_id)
            # 返回用户信息，排除密码
            return {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "disabled": user.disabled,
                "scopes": scopes,
                "client_id": client_id,
            }
        except Exception:
            # 如果获取用户信息失败，返回token payload
            return payload
    else:
        # client credentials流程，返回token payload
        return payload


@router.get("/admin/info")
async def get_admin_info(
    token: str = Depends(oauth2_auth_code_scheme)
):
    token_service = AppContainer.token_service()
    payload = token_service.validate_token(token)
    scopes = payload.get("scope", "")
    if "get_admin_info" not in scopes:
        raise HTTPException(status_code=403, detail="Insufficient scope")
    return payload