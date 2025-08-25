import asyncio
import httpx
from fastapi_book.utils import take_up_time


async def request_async(url):
    async with httpx.AsyncClient() as client:
        await client.get(url)
        


@take_up_time
async def run():
    tasks = [request_async("https://www.baidu.com") for _ in range(0, 50)]
    await asyncio.gather(*tasks)



if __name__ == "__main__":
    asyncio.run(run())
