import time
import requests
from concurrent.futures import ThreadPoolExecutor

URL = "http://127.0.0.1:8000/chat"


def send_request(i):

    start = time.perf_counter()

    response = requests.post(
        URL,
        json={
            "message": f"What is {i + 100} multiplied by 37?"
        },
        timeout=180
    )

    response.raise_for_status()

    elapsed = time.perf_counter() - start

    print(f"Request {i}: {elapsed:.2f}s")
    print(response.json())


start = time.perf_counter()

with ThreadPoolExecutor(max_workers=3) as executor:
    list(executor.map(send_request, range(3)))

print(
    f"\nTotal time: {time.perf_counter() - start:.2f}s"
)