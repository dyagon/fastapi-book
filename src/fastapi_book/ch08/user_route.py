
from fastapi import APIRouter, Depends, HTTPException

from .user_service import UserService
from .user_dto import UserCreateDTO, UserDTO

route = APIRouter()

@route.get("/user/{user_id}")
async def read_user(user_id: int, user_service: UserService = Depends()):
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@route.post("/user", response_model=UserDTO)
async def create_user(user: UserCreateDTO, user_service: UserService = Depends(UserService)):
    existing_user = await user_service.get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    existing_email = await user_service.get_user_by_email(user.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # In a real application, ensure to hash the password before storing it
    new_user = await user_service.create_user(user.username, user.email, user.password)
    return new_user