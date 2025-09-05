
import requests

from fastapi_book.utils import take_up_time

def request_sync(url):
    response = requests.get(url)
    return response


@take_up_time
def run():
    for _ in range(0, 50):
        request_sync("https://www.baidu.com")

if __name__ == "__main__":
    run()
