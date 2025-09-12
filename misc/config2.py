from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define a nested model for database settings
class DatabaseSettings(BaseSettings):
    user: str = 'default_user'
    password: str
    host: str = 'localhost'
    port: int = 5432
    db_name: str

# Define a nested model for server settings
class ServerSettings(BaseSettings):
    host: str = '127.0.0.1'
    port: int = 8000

# Main application settings model that brings everything together
class AppSettings(BaseSettings):
    """
    This is the main settings object for the application.
    It will automatically read from a .env file and environment variables.
    """
    app_name: str = 'My Awesome App'
    admin_email: EmailStr
    
    # Nest the other settings models
    db: DatabaseSettings
    server: ServerSettings
    db2: DatabaseSettings

    # Configure the sources and behavior for loading settings
    model_config = SettingsConfigDict(
        # Specify the env file to be used
        env_file='.env',
        # Specify the encoding of the env file
        env_file_encoding='utf-8',
        # The delimiter for nested models in the .env file
        # For example, DB__USER will map to db.user
        env_nested_delimiter='__',
        # Make reading environment variables case-insensitive
        case_sensitive=False,
        extra="ignore"
    )

# You can create a single instance to be imported across your application
settings = AppSettings()

import json

def main():
    print(f"Starting application: {settings.app_name}")
    print(f"Admin contact: {settings.admin_email}")
    print("-" * 20)

    # Accessing nested settings is intuitive
    print(f"Connecting to database '{settings.db.db_name}' on host '{settings.db.host}:{settings.db.port}' as user '{settings.db.user}'.")
    # Note: Never print passwords in a real app!
    print(f"Database password: {'*' * len(settings.db.password)}")
    print("-" * 20)
    
    print(f"Starting server on http://{settings.server.host}:{settings.server.port}")
    print("-" * 20)

    # You can also see the whole structure
    # The .model_dump_json() method is from Pydantic
    print("Full configuration object (as JSON):")
    print(json.dumps(settings.model_dump(), indent=2))


if __name__ == "__main__":
    main()
