from fastapi import APIRouter, Depends, HTTPException, Request


from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel

from jose import jwt, JWTError
from starlette.status import HTTP_401_UNAUTHORIZED

from ...domain.utils import TokenUtils

router = APIRouter()


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


oauth2_scheme = OAuth2ClientCredentialsBearer(tokenUrl="/authorize")


@router.get("/client", summary="Get Client Info, protected endpoint")
async def get_client_info(token: str = Depends(oauth2_scheme)):
    return TokenUtils.token_decode(token)

