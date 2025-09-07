from jose import jwt

from typing import Any

from fastapi_book import get_settings

class AuthToeknHelper:

    @staticmethod
    def token_encode(data: dict[str, Any]) -> str:
        return jwt.encode(
            data,
            key=get_settings().TOKEN_SIGN_SECRET,
            algorithm=get_settings().TOKEN_SIGN_ALGORITHM,
        )

    @staticmethod
    def token_decode(token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            key=get_settings().TOKEN_SIGN_SECRET,
            algorithms=get_settings().TOKEN_SIGN_ALGORITHM,
        )
