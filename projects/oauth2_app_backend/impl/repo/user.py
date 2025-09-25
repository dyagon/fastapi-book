import uuid
import asyncio

from sqlalchemy import Column, Integer, String, DateTime, TEXT, UUID, ForeignKey
from sqlalchemy import func
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB

from fastapi_book import Base

from ...domain.models.user import User, Authentication


class UserPO(Base):
    __tablename__ = "app_user"
    __table_args__ = {"schema": "oauth2"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True
    )
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
    user_uuid = Column(
        UUID(as_uuid=True), ForeignKey("oauth2.app_user.uuid"), nullable=False
    )

    provider = Column(String(20), nullable=False)
    provider_id = Column(String(20), nullable=False)

    credential = Column(JSONB)  # json
    user_info = Column(JSONB)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class UserRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_uuid(self, uuid: uuid.UUID) -> User | None:
        result = await self.db.execute(select(UserPO).where(UserPO.uuid == uuid))
        return User.model_validate(result.scalars().first())

    async def create_user(self, username: str, avatar_url: str) -> User:
        new_user = UserPO(uuid=uuid.uuid4(), username=username, avatar_url=avatar_url)
        self.db.add(new_user)
        await self.db.flush()
        return User.model_validate(new_user)

    async def update_user(self, uuid: uuid.UUID, username: str, avatar_url: str):
        stmt = update(UserPO).where(UserPO.uuid == uuid)
        stmt = stmt.values(username=username, avatar_url=avatar_url)
        await self.db.execute(stmt)
        return await self.get_user_by_uuid(uuid)

    async def delete_user(self, uuid: uuid.UUID):
        stmt = delete(UserPO).where(UserPO.uuid == uuid)
        await self.db.execute(stmt)

    async def get_user_authentications(
        self, user_uuid: uuid.UUID
    ) -> list[Authentication]:
        result = await self.db.execute(
            select(AuthenticationPO).where(AuthenticationPO.user_uuid == user_uuid)
        )
        return [Authentication.model_validate(auth) for auth in result.scalars().all()]

    async def get_auth(self, provider: str, provider_id: str) -> Authentication | None:
        result = await self.db.execute(
            select(AuthenticationPO).where(
                AuthenticationPO.provider == provider,
                AuthenticationPO.provider_id == provider_id,
            )
        )
        return Authentication.model_validate(result.scalars().first())

    async def get_auth_by_provider(
        self, provider: str, uuid: uuid.UUID
    ) -> Authentication | None:
        result = await self.db.execute(
            select(AuthenticationPO).where(
                AuthenticationPO.provider == provider,
                AuthenticationPO.user_uuid == uuid,
            )
        )
        return Authentication.model_validate(result.scalars().first())

    async def get_auth_by_provider_for_update(
        self, provider: str, uuid: uuid.UUID
    ) -> Authentication | None:
        result = await self.db.execute(
            select(AuthenticationPO)
            .where(
                AuthenticationPO.provider == provider,
                AuthenticationPO.user_uuid == uuid,
            )
            .with_for_update()
        )
        return Authentication.model_validate(result.scalars().first())

    async def get_user_and_auths(
        self, uuid: uuid.UUID
    ) -> tuple[User | None, list[Authentication] | None]:
        user, auths = await asyncio.gather(
            self.get_user_by_uuid(uuid), self.get_user_authentications(uuid)
        )
        return user, auths

    async def get_user_and_auth(
        self, uuid: uuid.UUID, provider: str
    ) -> tuple[User | None, Authentication | None]:
        user, auth = await asyncio.gather(
            self.get_user_by_uuid(uuid), self.get_auth_by_provider(provider, uuid)
        )
        return user, auth

    async def get_user_and_auth_for_update(
        self, uuid: uuid.UUID, provider: str
    ) -> tuple[User | None, Authentication | None]:
        user, auth = await asyncio.gather(
            self.get_user_by_uuid(uuid),
            self.get_auth_by_provider_for_update(provider, uuid),
        )
        return user, auth

    async def create_authentication(
        self,
        user_uuid: uuid.UUID,
        provider: str,
        provider_id: str,
        credential: dict,
        user_info: dict,
    ) -> Authentication:
        new_authentication = AuthenticationPO(
            user_uuid=user_uuid,
            provider=provider,
            provider_id=provider_id,
            credential=credential,
            user_info=user_info,
        )
        self.db.add(new_authentication)
        await self.db.flush()
        print(new_authentication)
        return Authentication.model_validate(new_authentication)

    async def update_authentication(
        self, provider: str, provider_id: str, credential: dict
    ) -> Authentication:
        stmt = update(AuthenticationPO).where(
            AuthenticationPO.provider == provider,
            AuthenticationPO.provider_id == provider_id,
        )
        stmt = stmt.values(credential=credential)
        await self.db.execute(stmt)
        return await self.get_auth(provider, provider_id)

    async def delete_authentication(self, provider: str, provider_id: str):
        stmt = delete(AuthenticationPO).where(
            AuthenticationPO.provider == provider,
            AuthenticationPO.provider_id == provider_id,
        )
        await self.db.execute(stmt)
        await self.db.commit()
