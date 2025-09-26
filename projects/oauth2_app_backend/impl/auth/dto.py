import time

from pydantic import BaseModel, model_validator
from typing import Optional, Any


class Token(BaseModel):
    access_token: str
    expires_in: int
    expires_at: int
    token_type: str
    scope: str
    refresh_token: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def set_expires_at(cls, data: Any) -> Any:
        """
        Sets 'expires_at' from 'expires_in' if it's not already provided.
        """
        # Ensure data is a dict to work with
        if isinstance(data, dict):
            # If 'expires_at' is missing but 'expires_in' is present...
            if 'expires_at' not in data and 'expires_in' in data:
                # Calculate expires_at and add it to the data
                data['expires_at'] = data['expires_in'] + int(time.time())
        # Always return the data for further validation
        return data

    def is_expired(self) -> bool:
        return time.time() > self.expires_at - 60  # add 60 seconds buffer


class UserInfoDto(BaseModel):
    id: str
    username: str
    email: Optional[str]
    full_name: Optional[str]