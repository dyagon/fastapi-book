import uuid

from sqlalchemy import Column, Integer, String, DateTime, TEXT, func

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_book import Base

from ...domain.models.user import User, Authentication


class UserPO(Base):
    __tablename__ = "app_user"
    __table_args__ = {"schema": "oauth2"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, nullable=False, index=True)
    username = Column(String(20))
    avatar_url = Column(String(255))

    created_at = Column(DateTime, default=func.now())

    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "username": self.username,
            "avatar_url": self.avatar_url,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class AuthenticationPO(Base):
    __tablename__ = "app_authentication"
    __table_args__ = {"schema": "oauth2"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    provider = Column(String(20), nullable=False)
    provider_id = Column(String(20), nullable=False)

    credentials = Column(TEXT)  # json

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserRepo:
    def __init__(self, db: AsyncSession):
        print(db)
        if type(db) != AsyncSession:
            print(type(db))
            raise ValueError("db must be an AsyncSession")
        self.db = db

    async def get_user_by_uuid(self, uuid: str) -> User | None:
        result = await self.db.execute(select(UserPO).where(UserPO.uuid == uuid))
        return result.scalars().first()

    async def create_user(self, username: str, avatar_url: str) -> User:
        new_user = UserPO(
            uuid=str(uuid.uuid4()), username=username, avatar_url=avatar_url
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return User.model_validate(new_user)

    async def update_user(self, uuid: str, username: str, avatar_url: str):
        stmt = update(UserPO).where(UserPO.uuid == uuid)
        stmt = stmt.values(username=username, avatar_url=avatar_url)
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_user_by_uuid(uuid)

    async def delete_user(self, uuid: str):
        stmt = delete(UserPO).where(UserPO.uuid == uuid)
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_auth(self, provider: str, provider_id: str) -> Authentication | None:
        result = await self.db.execute(
            select(AuthenticationPO).where(
                AuthenticationPO.provider == provider,
                AuthenticationPO.provider_id == provider_id,
            )
        )
        return result.scalars().first()

    async def create_authentication(
        self, user_id: int, provider: str, provider_id: str, credentials: dict
    ) -> Authentication:
        new_authentication = AuthenticationPO(
            user_id=user_id,
            provider=provider,
            provider_id=provider_id,
            credentials=credentials,
        )
        self.db.add(new_authentication)
        await self.db.commit()
        await self.db.refresh(new_authentication)
        return Authentication.model_validate(new_authentication)

    async def update_authentication(
        self, user_id: int, provider: str, provider_id: str, credentials: dict
    ) -> Authentication:
        stmt = update(AuthenticationPO).where(
            AuthenticationPO.user_id == user_id,
            AuthenticationPO.provider == provider,
            AuthenticationPO.provider_id == provider_id,
        )
        stmt = stmt.values(credentials=credentials)
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_auth(provider, provider_id)

    async def delete_authentication(
        self, user_id: int, provider: str, provider_id: str
    ):
        stmt = delete(AuthenticationPO).where(
            AuthenticationPO.user_id == user_id,
            AuthenticationPO.provider == provider,
            AuthenticationPO.provider_id == provider_id,
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def get_user_authentications(self, user_id: int) -> list[Authentication]:
        result = await self.db.execute(
            select(AuthenticationPO).where(AuthenticationPO.user_id == user_id)
        )
        return result.scalars().all()
