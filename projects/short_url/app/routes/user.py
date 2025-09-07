from fastapi import APIRouter, Depends, HTTPException

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from datetime import datetime, timedelta, timezone

from ..dto import SingleShortUrlCreateDTO
from ..depends import get_user_service, get_short_service, UserService, ShortService
from ...infra.utils import AuthTokenHelper, PasslibHelper, generate_short_url

router_user = APIRouter(prefix="/api/v1", tags=["manage"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/oauth2/authorize")


@router_user.post("/oauth2/authorize", summary="OAuth2 - Authorization")
async def login(
    user_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
):
    if not user_data:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail="Invalid user data"
        )
    user_info = await user_service.get_user_by_name(user_data.username)

    if not user_info:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="User not found")

    if not PasslibHelper.verify_password(user_data.password, user_info.password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    # jwt token
    data = {
        "iss": user_info.username,
        "sub": "hello world",
        "username": user_info.username,
        "admin": True,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    token = AuthTokenHelper.token_encode(data)

    return {"access_token": token, "token_type": "bearer"}


@router_user.post("/create/single/short", summary="Create single short URL")
async def create_single_short_url(
    create_dto: SingleShortUrlCreateDTO,
    token: str = Depends(oauth2_scheme),
    short_service: ShortService = Depends(get_short_service),
):
    payload = AuthTokenHelper.token_decode(token)
    if not payload:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Invalid authentication token"
        )
    
    create_dto.short_tag = generate_short_url()
    create_dto.short_url = f"{create_dto.short_url}{create_dto.short_tag}"
    create_dto.created_by = payload.get("username")
    create_dto.msg_content = f"hello, click {create_dto.short_url}"
    print(create_dto)
    result = await short_service.create_short_url(**create_dto.model_dump())
    return {"code": 200, "msg": "Short URL created successfully", "data": result}
