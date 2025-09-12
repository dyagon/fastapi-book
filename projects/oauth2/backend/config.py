from pydantic_settings import BaseSettings



class Config(BaseSettings):

    # auth code
    AUTH_CODE_CLIENT_ID: str = "auth-code-client"
    AUTH_CODE_CLIENT_SECRET: str = "auth-code-secret-123"

    # client credentials
    CLIENT_ID: str = "client-credentials-client"
    CLIENT_SECRET: str = "client-credentials-secret-456"

    AUTH_SERVER_BASE_URL: str = "http://localhost:8000"
    RESOURCE_SERVER_BASE_URL: str = "http://localhost:8000/api"
    CLIENT_BASE_URL: str = "http://localhost:8001"
    REDIRECT_URI: str = f"{CLIENT_BASE_URL}/callback"



config = Config()