from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from openai import AsyncOpenAI

from src.models.schemas import ChatRequest, ChatResponse

import httpx

import logging
import asyncio
import random

from fastapi import HTTPException
from openai import (
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)

logger = logging.getLogger(__name__)

MODEL_NAME = "Qwen/Qwen3-1.7B"


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create asynchronous HTTP client
    app.state.llm_client = AsyncOpenAI(
        base_url="http://127.0.0.1:8001/v1",
        api_key="not-needed",
        timeout=httpx.Timeout(20,connect=3),
        max_retries=0
    )

    try:
        yield
    finally:
        # Close HTTP connections
        await app.state.llm_client.close()


app = FastAPI(lifespan=lifespan)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):

    client = http_request.app.state.llm_client
    
    messages = [
        {
            "role": "user",
            "content": request.message
        }
    ]

    try:
        response = await generate_with_retry(client, messages)

        answer = response.choices[0].message.content or ""

        return ChatResponse(answer=answer)
    
    except APITimeoutError as e:
        raise HTTPException(
            status_code=504,
            detail="Inference server timed out"
        ) from e

    except APIConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail="Inference server unavailable"
        ) from e

    except APIStatusError as e:
        raise HTTPException(
            status_code=502,
            detail="Inference server returned an error"
        ) from e


RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


async def generate_with_retry(client, messages):

    max_attempts = 3
    base_delay = 1.0
    max_delay = 10.0


    for attempt in range(1, max_attempts + 1):

        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=200
            )

            return response

        except (APITimeoutError, APIConnectionError) as e:
            if attempt == max_attempts:
                raise

        except APIStatusError as e:
            if (
                e.status_code not in RETRYABLE_STATUS_CODES
                or attempt == max_attempts
            ):
                raise

        # Exponential backoff
        backoff = min(
            max_delay,
            base_delay * (2 ** (attempt - 1))
        )

        # Full jitter
        delay = random.uniform(0, backoff)

        logger.warning(
            "Attempt %d/%d failed. Retrying in %.2f seconds",
            attempt,
            max_attempts,
            delay
        )

        await asyncio.sleep(delay)


