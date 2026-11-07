import asyncio
import time

import httpx


URL = "http://127.0.0.1:8000/chat/stream"
NUM_REQUESTS = 5


async def send_request(client, request_id):
    start = time.perf_counter()
    first_token_time = None
    chunks = []

    async with client.stream(
        "POST",
        URL,
        json={
            "message": f"Explain concept number {request_id}: "
                       "How does attention work in transformers? "
                       "Answer in about 100 words."
        },
    ) as response:

        response.raise_for_status()

        async for chunk in response.aiter_text():
            if not chunk:
                continue

            if first_token_time is None:
                first_token_time = time.perf_counter()

            chunks.append(chunk)

    end = time.perf_counter()

    ttft = (
        first_token_time - start
        if first_token_time is not None
        else None
    )

    print(
        f"Request {request_id}: "
        f"TTFT={ttft:.2f}s, "
        f"Total={end - start:.2f}s, "
        f"Chars={len(''.join(chunks))}"
    )

    return end - start


async def main():
    start = time.perf_counter()

    async with httpx.AsyncClient(timeout=180.0) as client:
        durations = await asyncio.gather(
            *(send_request(client, i) for i in range(NUM_REQUESTS))
        )

    total_time = time.perf_counter() - start

    print(f"\nCompleted requests: {len(durations)}")
    print(f"Total wall time: {total_time:.2f}s")


if __name__ == "__main__":
    asyncio.run(main())