from jose import jwt, JWTError

from pydantic import ValidationError
from .exception import UnauthorizedClientException

SECRET_KEY = "0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
ALGORITHM = "HS256"


class TokenUtils:
    @staticmethod
    def token_encode(data: dict) -> str:
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def token_decode(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except (JWTError, ValidationError):
            raise UnauthorizedClientException("Could not validate credentials")

