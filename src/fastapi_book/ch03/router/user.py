from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
import json


router = APIRouter()


# Pydantic models for request bodies
class User(BaseModel):
    name: str
    email: EmailStr
    age: int
    is_active: bool = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    is_active: Optional[bool] = None


class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str


class UserWithAddress(BaseModel):
    user: User
    address: Address
    tags: List[str] = []


@router.get("/user/useId", tags=["user"])
async def get_user():
    return {"user_id": 1, "name": "user_1"}


@router.get("/user/{user_id}", tags=["user"])
async def get_user_by_id(user_id: int, sex: str, age: int = 20):
    return {"user_id": user_id, "name": f"user_{user_id}", "sex": sex, "age": age}


# POST with JSON body
@router.post("/user", tags=["user"])
async def create_user(user: User):
    """Create a new user with JSON body"""
    return {
        "message": "User created successfully",
        "user": user,
        "created_at": datetime.now().isoformat()
    }


# POST with complex nested JSON
@router.post("/user/with-address", tags=["user"])
async def create_user_with_address(user_data: UserWithAddress):
    """Create user with nested address and tags"""
    return {
        "message": "User with address created successfully",
        "data": user_data,
        "created_at": datetime.now().isoformat()
    }


# PUT with JSON body for updates
@router.put("/user/{user_id}", tags=["user"])
async def update_user(user_id: int, user_update: UserUpdate):
    """Update user with partial data"""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    return {
        "message": f"User {user_id} updated successfully",
        "updated_fields": user_update.dict(exclude_unset=True),
        "updated_at": datetime.now().isoformat()
    }


# POST with form data
@router.post("/user/form", tags=["user"])
async def create_user_form(
    name: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    is_active: bool = Form(True),
    bio: Optional[str] = Form(None)
):
    """Create user using form data instead of JSON"""
    return {
        "message": "User created from form data",
        "user": {
            "name": name,
            "email": email,
            "age": age,
            "is_active": is_active,
            "bio": bio
        },
        "created_at": datetime.now().isoformat()
    }


# POST with file upload
@router.post("/user/avatar", tags=["user"])
async def upload_user_avatar(
    user_id: int = Form(...),
    file: UploadFile = File(...)
):
    """Upload user avatar image"""
    # Check file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content (in real app, you'd save to storage)
    content = await file.read()
    
    return {
        "message": "Avatar uploaded successfully",
        "user_id": user_id,
        "filename": file.filename,
        "content_type": file.content_type,
        "file_size": len(content),
        "uploaded_at": datetime.now().isoformat()
    }


# POST with multiple files
@router.post("/user/documents", tags=["user"])
async def upload_user_documents(
    user_id: int = Form(...),
    files: List[UploadFile] = File(...)
):
    """Upload multiple documents for a user"""
    if len(files) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 files allowed")
    
    uploaded_files = []
    for file in files:
        content = await file.read()
        uploaded_files.append({
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content)
        })
    
    return {
        "message": f"{len(files)} documents uploaded successfully",
        "user_id": user_id,
        "files": uploaded_files,
        "uploaded_at": datetime.now().isoformat()
    }


# POST with mixed form data and file
@router.post("/user/profile", tags=["user"])
async def create_user_profile(
    name: str = Form(...),
    email: str = Form(...),
    age: int = Form(...),
    bio: str = Form(None),
    profile_picture: Optional[UploadFile] = File(None),
    tags: str = Form("[]")  # JSON string for complex data in forms
):
    """Create user profile with form data and optional profile picture"""
    try:
        # Parse tags from JSON string
        parsed_tags = json.loads(tags)
    except json.JSONDecodeError:
        parsed_tags = []
    
    result = {
        "message": "User profile created successfully",
        "user": {
            "name": name,
            "email": email,
            "age": age,
            "bio": bio,
            "tags": parsed_tags
        },
        "created_at": datetime.now().isoformat()
    }
    
    if profile_picture:
        if not profile_picture.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Profile picture must be an image")
        
        content = await profile_picture.read()
        result["profile_picture"] = {
            "filename": profile_picture.filename,
            "content_type": profile_picture.content_type,
            "file_size": len(content)
        }
    
    return result
