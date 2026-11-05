import asyncio
import random
import time
import uuid
import os

import httpx
import structlog

from dotenv import load_dotenv

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException

from openai import (
    AsyncOpenAI,
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)

from src.models.schemas import ChatRequest, ChatResponse
from src.api.logging_config import setup_logging


# ============================================================
# Configuration
# ============================================================


load_dotenv()

MODEL_NAME = os.environ["LLM_MODEL"]
VLLM_BASE_URL = os.environ["LLM_BASE_URL"]
LLM_API_KEY = os.getenv("LLM_API_KEY", "not-needed")

MAX_ATTEMPTS = 3
BASE_DELAY = 1.0
MAX_DELAY = 10.0

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}



# ============================================================
# Structured Logging
# ============================================================

setup_logging()

logger = structlog.get_logger("ai_api")


# ============================================================
# Application Lifespan
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("application_starting")

    app.state.llm_client = AsyncOpenAI(
        base_url=VLLM_BASE_URL,
        api_key=LLM_API_KEY,
        timeout=httpx.Timeout(
            20.0,
            connect=3.0
        ),
        max_retries=0
    )

    logger.info(
        "llm_client_initialized",
        model=MODEL_NAME,
        base_url=VLLM_BASE_URL
    )

    try:
        yield

    finally:
        await app.state.llm_client.close()

        logger.info("application_shutdown")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="AI Research Assistant",
    description="FastAPI + AsyncOpenAI + vLLM",
    version="0.1.0",
    lifespan=lifespan
)


# ============================================================
# Retry Logic
# ============================================================

async def generate_with_retry(client, messages):

    for attempt in range(1, MAX_ATTEMPTS + 1):

        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=200
            )

            return response

        except (APITimeoutError, APIConnectionError) as e:

            if attempt == MAX_ATTEMPTS:
                raise

            error_type = type(e).__name__

        except APIStatusError as e:

            if (
                e.status_code not in RETRYABLE_STATUS_CODES
                or attempt == MAX_ATTEMPTS
            ):
                raise

            error_type = type(e).__name__

        # Exponential backoff
        backoff = min(
            MAX_DELAY,
            BASE_DELAY * (2 ** (attempt - 1))
        )

        # Full jitter
        delay = random.uniform(0, backoff)

        logger.warning(
            "llm_retry",
            attempt=attempt,
            max_attempts=MAX_ATTEMPTS,
            error_type=error_type,
            delay_seconds=round(delay, 2)
        )

        await asyncio.sleep(delay)


# ============================================================
# Health Endpoint
# ============================================================

@app.get("/")
async def root():

    return {
        "message": "AI Research Assistant API is running"
    }


# ============================================================
# Chat Endpoint
# ============================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):

    # Generate unique request ID
    request_id = str(uuid.uuid4())

    # Bind request ID to the current async context
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id
    )

    start = time.perf_counter()

    client = http_request.app.state.llm_client

    messages = [
        {
            "role": "user",
            "content": request.message
        }
    ]

    logger.info(
        "request_started",
        model=MODEL_NAME
    )

    status_code = 500

    try:

        response = await generate_with_retry(
            client,
            messages
        )

        answer = response.choices[0].message.content or ""

        status_code = 200

        logger.info(
            "llm_generation_completed",
            model=MODEL_NAME,
            prompt_tokens=(
                response.usage.prompt_tokens
                if response.usage else None
            ),
            completion_tokens=(
                response.usage.completion_tokens
                if response.usage else None
            )
        )

        return ChatResponse(answer=answer)

    except APITimeoutError as e:

        status_code = 504

        logger.warning(
            "llm_timeout",
            error_type=type(e).__name__
        )

        raise HTTPException(
            status_code=504,
            detail="Inference server timed out"
        ) from e

    except APIConnectionError as e:

        status_code = 503

        logger.warning(
            "llm_connection_failed",
            error_type=type(e).__name__
        )

        raise HTTPException(
            status_code=503,
            detail="Inference server unavailable"
        ) from e

    except APIStatusError as e:

        status_code = 502

        logger.error(
            "llm_upstream_error",
            upstream_status=e.status_code
        )

        raise HTTPException(
            status_code=502,
            detail="Inference server returned an error"
        ) from e

    except Exception as e:

        logger.exception(
            "unexpected_error",
            error_type=type(e).__name__
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) from e

    finally:

        duration_ms = round(
            (time.perf_counter() - start) * 1000,
            2
        )

        logger.info(
            "request_finished",
            status_code=status_code,
            duration_ms=duration_ms
        )




        