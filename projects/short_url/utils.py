import random
import string
from jose import jwt, JWTError

from passlib.context import CryptContext

from .config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = get_settings().TOKEN_SIGN_SECRET
ALGORITHM = "HS256"

class PasslibHelper:

    @staticmethod
    def hash_password(plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    

class AuthTokenHelper:

    @staticmethod
    def token_encode(data: dict) -> str:
        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def token_decode(token: str) -> dict:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None


def generate_short_url(length: int = 6) -> str:
    """
    Generate a random short URL string.
    
    Args:
        length (int): The length of the short URL string. Default is 6.
        
    Returns:
        str: A random string containing alphanumeric characters.
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))