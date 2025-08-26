import aiofiles
import os
from fastapi import File, UploadFile, HTTPException

from fastapi import APIRouter

router = APIRouter()

@router.post("/upload-and-save")
async def upload_and_save(file: UploadFile = File(...)):
    """
    1. Receive file via FastAPI's File (HTTP upload)
    2. Save it to disk using aiofiles (filesystem I/O)
    """
    
    # Validate file
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "Only images allowed")
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Save uploaded file to disk using aiofiles
    file_path = f"uploads/{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    return {
        "message": "File uploaded and saved",
        "filename": file.filename,
        "saved_to": file_path,
        "size": len(content)
    }

@router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Read file from disk using aiofiles and return content
    """
    file_path = f"uploads/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    
    # Read file from disk using aiofiles
    async with aiofiles.open(file_path, "rb") as f:
        content = await f.read()
    
    return {"filename": filename, "content_length": len(content)}


@router.post("/sync_files")
def sync_file_operation(files: list[UploadFile] = File(...)):
    """
    Synchronous file operation example
    :param files: List of uploaded files
    :return: Filenames and count
    """
    return {"num_files": len(files), "filenames": [file.filename for file in files]}