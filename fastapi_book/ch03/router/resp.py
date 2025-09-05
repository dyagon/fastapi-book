from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import time
import os
import aiofiles

router = APIRouter(tags=["response"])


async def slow_data_generator():
    """
    An async generator that yields data chunks slowly.
    This simulates a long-running process, like querying a database,
    calling external APIs, or generating a large report.
    """
    for i in range(10):
        # Yield a chunk of data
        yield f"data: {i} @ {time.time()}\n\n"
        # Simulate I/O-bound work (like a database call or API request)
        await asyncio.sleep(1)


@router.get("/stream-data")
async def stream_data():
    """
    Streams generated data to the client.
    The client will receive data chunks as they are generated,
    without waiting for the entire response to be ready.
    
    How to use it:
    You can consume this with JavaScript's `fetch` API and a `ReadableStream`:
    
    const response = await fetch('/stream-data');
    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        console.log(decoder.decode(value));
    }
    """
    return StreamingResponse(slow_data_generator(), media_type="text/event-stream")


async def file_chunk_generator(file_path: str, chunk_size: int = 1024 * 1024):
    """
    An async generator that reads a file in chunks.
    This is memory-efficient for large files as it doesn't load the whole file into memory.
    """
    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(chunk_size):
            yield chunk


@router.get("/stream-file/{filename}")
async def stream_file(filename: str):
    """
    Streams a large file from the server's disk.
    This is useful for serving large downloads without high memory usage.
    
    To test this, first create a large dummy file. You can do this
    from your terminal:
    
    `fallocate -l 100M large_file.bin` or `mkfile 100m large_file.bin`
    
    Then, access this endpoint: /stream-file/large_file.bin
    """
    file_path = f"./{filename}"  # Assumes file is in the project root
    if not os.path.exists(file_path):
        return {"error": "File not found"}, 404

    return StreamingResponse(
        file_chunk_generator(file_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
