from fastapi import Depends


from ..domain.service import OAuth2Service, ClientRepo, UserRepo

from ..impl.token_manager import TokenManager

from ..context import infra


async def get_token_manager() -> TokenManager:
    return TokenManager(infra.redis.get_redis())


async def get_oauth2_service(
    token_manager: TokenManager = Depends(get_token_manager),
) -> OAuth2Service:
    return OAuth2Service(ClientRepo(), UserRepo(), token_manager)
