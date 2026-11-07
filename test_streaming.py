import asyncio
from openai import AsyncOpenAI


async def main():

    async with AsyncOpenAI(
        base_url="http://127.0.0.1:8001/v1",
        api_key="not-needed"
    ) as client:

        stream = await client.chat.completions.create(
            model="Qwen/Qwen3-1.7B",
            messages=[
                {
                    "role": "user",
                    "content": "Explain transformers in 100 words."
                }
            ],
            max_tokens=200,
            stream=True
        )

        async for chunk in stream:

            content = chunk.choices[0].delta.content

            if content:
                print(content, end="", flush=True)

        print()


if __name__ == "__main__":
    asyncio.run(main())