import asyncio
import time
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://127.0.0.1:8001/v1",
    api_key="not-needed"
)

MODEL = "Qwen/Qwen3-1.7B"


async def send_request(i):
    start = time.perf_counter()

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Explain {['transformers', 'attention', 'RAG'][i]} "
                    "in detail with examples."
                )
            }
        ],
        max_tokens=300
    )

    elapsed = time.perf_counter() - start

    usage = response.usage

    print(
        f"Request {i}: "
        f"Time={elapsed:.2f}s, "
        f"Input={usage.prompt_tokens}, "
        f"Output={usage.completion_tokens}, "
        f"Tokens/sec={usage.completion_tokens / elapsed:.2f}"
    )

    return response


async def main():

    # Warm-up
    await send_request(0)

    # ---------------------------
    # Sequential Benchmark
    # ---------------------------

    print("\n--- SEQUENTIAL ---")

    start = time.perf_counter()

    for i in range(3):
        await send_request(i)

    sequential_time = time.perf_counter() - start

    print(f"Sequential total: {sequential_time:.2f}s")

    # ---------------------------
    # Concurrent Benchmark
    # ---------------------------

    print("\n--- CONCURRENT ---")

    start = time.perf_counter()

    await asyncio.gather(
        send_request(0),
        send_request(1),
        send_request(2)
    )

    concurrent_time = time.perf_counter() - start

    print(f"Concurrent total: {concurrent_time:.2f}s")

    # ---------------------------
    # Comparison
    # ---------------------------

    print("\n--- RESULTS ---")

    print(f"Sequential: {sequential_time:.2f}s")
    print(f"Concurrent: {concurrent_time:.2f}s")

    print(
        f"Speedup: {sequential_time / concurrent_time:.2f}x"
    )

    print(
        f"Sequential throughput: {900 / sequential_time:.2f} tokens/s"
    )

    print(
        f"Concurrent throughput: {900 / concurrent_time:.2f} tokens/s"
    )


if __name__ == "__main__":
    asyncio.run(main())