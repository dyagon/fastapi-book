

from .models import Apps, Users, UserIdentities, AuthCodes, AccessTokens


APPS_DB: dict[str, Apps] = {
    "1234567890": Apps(
        app_id="1234567890",
        app_secret="1234567890",
        owner_developer_id="1234567890",
        authorized_redirect_uris=["http://localhost:8000/wechat/oauth/callback"]
    )
}

USERS_DB: dict[str, Users] = {
    "1234567890": Users(
        internal_user_id="1234567890",
        nickname="1234567890",
        avatar_url="http://localhost:8000/wechat/oauth/callback"
    )
}

USER_IDENTITIES_DB: dict[str, UserIdentities] = {
    "1234567890": UserIdentities(
        app_id="1234567890",
        internal_user_id="1234567890",
        union_id="1234567890",
        open_id="1234567890"
    )
}

AUTH_CODES_DB: dict[str, AuthCodes] = {
    "1234567890": AuthCodes(
        internal_user_id="1234567890",
        app_id="1234567890",
        scope="1234567890",
        is_used=False,
        expires_at=1234567890
    )
}

ACCESS_TOKENS_DB: dict[str, AccessTokens] = {
    "1234567890": AccessTokens(
        union_id="1234567890",
        open_id="1234567890",
        scope="1234567890",
        expires_at=1234567890
    )
}

class OAuthRepository:
    def __init__(self):
        pass 


class AppsRepository:
    def __init__(self):
        pass

class UsersRepository:
    def __init__(self):
        pass

class UserIdentitiesRepository:
    def __init__(self):
        pass

class AuthCodesRepository:
    def __init__(self):
        pass

class AccessTokensRepository:
    def __init__(self):
        pass