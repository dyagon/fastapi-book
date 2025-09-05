from fastapi import FastAPI
from pydantic import BaseModel, Field, model_validator

app = FastAPI(
    title="FastAPI Book Chapter 5",
    description="Chapter 5 Example for FastAPI Book",
    docs_url=None,
    redoc_url=None,
    version="0.1.0",
)


class User(BaseModel):
    username: str = Field(
        ...,
        title="The username of the user",
        min_length=3,
        max_length=12,
        pattern="^[a-zA-Z0-9]+$",
        examples=["alice", "bob123"],
        description="Must be alphanumeric and between 3 to 12 characters",
    )

    age: int =Field(
        ...,
        title="The age of the user",
        ge=18,
        le=100,
        examples=[25, 30],
        description="Must be between 18 and 100",
    )
    password_old: str = Field(
        ...,
        title="The password of the user",
        min_length=6,
        max_length=20,
        examples=["pass123", "abc456xyz"],
        description="Must be between 6 to 20 characters",
    )
    password_new: str = Field(
        ...,
        title="The new password of the user",
        min_length=6,
        max_length=20,
        examples=["newpass123", "newabc456xyz"],
        description="Must be between 6 to 20 characters",
    )

    @model_validator(mode='after')
    def passwords_different(self) -> 'User':
        if self.password_old == self.password_new:
            raise ValueError("New password must be different from the old password")
        return self


@app.post("/users/", tags=["users"])
async def create_user(user: User):
    return {
        'username': user.username,
        'age': user.age,
        'password_old': user.password_old,
        'password_new': user.password_new,
    }

