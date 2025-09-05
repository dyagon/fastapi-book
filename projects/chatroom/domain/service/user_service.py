
from ...impl import UserRepository
from ...infra import AuthToeknHelper

from datetime import datetime, timedelta, timezone

class UserService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_phone(self, phone_number: str):
        """通过电话号码获取用户"""
        return await self.user_repo.get_user_by_phone(phone_number)

    async def register_user(self, phone_number: str, password: str, username: str):
        """注册用户"""
        result = await self.user_repo.get_user_by_phone(phone_number)
        if result:
            raise ValueError("Phone number already registered")
        user = await self.user_repo.create_user(
            phone_number=phone_number,
            password=password,
            username=username
        )
        return user
    
    async def authenticate_and_issue_token(self, phone_number: str, password: str) -> str:
        """验证用户并签发令牌"""
        user = await self.user_repo.get_user_by_phone(phone_number)
        if not user or user.password != password:
            raise ValueError("Invalid phone number or password")
        
        data = {
            "iss": user.phone_number,
            "sub": str(user.id),
            "phone_number": user.phone_number,
            "username": user.username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=2)  # 令牌有效期2小时
        }
        
        return AuthToeknHelper.token_encode(data)