import pathlib
from fastapi import APIRouter, Depends

from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse
from ..dto import RegisterAaction, LoginAaction
from ..depends import get_user_service, UserService

router = APIRouter(prefix="/api/v1/user", tags=["用户登入API接口"])

templates_dir = pathlib.Path(__file__).parent.parent / "templates"

@router.get("/register")
async def index():
    return FileResponse(templates_dir / "register.html")


@router.get("/register_action")
async def register(user: RegisterAaction = Depends(), user_servcie: UserService = Depends(get_user_service)):
    # 判断是否已经注册
    result = await user_servcie.get_user_by_phone(user.phone_number)
    if not result:
        # 没有注册则注册并写入数据库
        await user_servcie.register_user(phone_number=user.phone_number, password=user.password,
                                         username=user.username)
        return RedirectResponse("/api/v1/user/login")
    else:
        return PlainTextResponse("该用户已注册过了！请重新输入账号信息")


@router.get("/login")
async def login():
    return FileResponse(templates_dir / "login.html")


@router.get("/login_action")
async def login_action(user: LoginAaction = Depends(), user_servcie: UserService = Depends(get_user_service)):
    try:
        token = await user_servcie.authenticate_and_issue_token(phone_number=user.phone_number, password=user.password)
        return RedirectResponse(f"http://127.0.0.1:8000/api/v1/room/online?token={token}")
    except Exception as e:
        return PlainTextResponse(str(e))
