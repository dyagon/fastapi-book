from ..impl.auth.dto import Token
from ..domain.models.credential import LocalOAuthInfo
from ..domain.models.user import User
from ..context.app_container import Container


async def get_user_and_auths(session_data: dict):
    if not session_data or not session_data.get("session_id"):
        return None, None

    async with Container.user_service() as user_service:
        user, auths = await user_service.get_user_and_auths(session_data.get("user_id"))
        return user, auths


async def get_local_oauth_info(
    session_data: dict, provider: str
) -> tuple[User | None, Token | None]:
    if not session_data or not session_data.get("session_id"):
        return None, None

    async with Container.user_service() as user_service:
        user, auth = await user_service.get_user_and_auth(
            session_data.get("user_id"), provider
        )
        return user, LocalOAuthInfo(token=auth.credential, user_info=auth.user_info)
