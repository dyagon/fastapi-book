from passlib.context import CryptContext

# Initialize password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


users = {
    "alice": {
        "id": "1",
        "username": "alice",
        "password": pwd_context.hash("123"),  # Hash the password
        "full_name": "Alice Wonderland",
        "email": "alice@example.com",
        "disabled": False,
    },
    "bob": {
        "id": "2",
        "username": "bob",
        "password": pwd_context.hash("123"),
        "full_name": "Bob Builder",
        "email": "bob@example.com",
        "disabled": False,
    },
}

clients = {
    "client-credentials-client": {
        "client_id": "client-credentials-client",
        "client_secret": "client-credentials-secret-456",
        "redirect_uris": [],  # Not needed for client credentials
        "scopes": ["get_admin_info", "get_user_info", "get_client_info"],
        "client_type": "confidential",
    },
    "auth-code-client": {
        "client_id": "auth-code-client",
        "client_secret": "auth-code-secret-123",
        "redirect_uris": [
            "http://localhost:8001/callback",
            "http://127.0.0.1:8001/callback",
        ],
        "scopes": ["get_admin_info", "get_user_info", "get_client_info"],
        "client_type": "confidential",  # confidential or public
    },
    "pkce-public-client": {
        "client_id": "pkce-public-client",
        "client_secret": None,  # Public clients don't have secrets
        "redirect_uris": [
            "http://localhost:8002/callback",
            "http://127.0.0.1:8002/callback",
        ],
        "scopes": ["get_admin_info", "get_user_info", "get_client_info"],
        "client_type": "public",
    },
}
