from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from config import LLM_MODEL, HF_TOKEN
from src.llm.client import LLMClient
from src.llm.prompts import TOOL_SYSTEM_PROMPT
from src.agent.agent import Agent
from src.models.schemas import ChatRequest, ChatResponse

import logging
from fastapi import HTTPException

import asyncio
import time


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Loading Qwen model...")

    llm = LLMClient(
        LLM_MODEL,
        hf_token=HF_TOKEN
    )

    app.state.agent = Agent(
        llm=llm,
        max_iterations=6
    )

    app.state.inference_semaphore = asyncio.Semaphore(1)

    print("Qwen model loaded successfully!")

    yield

    print('\n\n\n\nEnding here----------------\n\n\n')
    # Cleanup happens here during shutdown
    app.state.agent = None


app = FastAPI(
    title="AI Research Assistant",
    description="An AI assistant powered by Qwen and custom tools",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "message": "AI Research Assistant API is running"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, http_request: Request):

    agent = http_request.app.state.agent

    messages = [
        {"role": "system", "content": TOOL_SYSTEM_PROMPT},
        {"role": "user", "content": request.message}
    ]

    try:
        print("Request waiting for GPU access...")

        async with http_request.app.state.inference_semaphore:

            print("GPU access acquired")

            answer = await asyncio.to_thread(
                agent.run,
                messages
            )

        return ChatResponse(answer=answer)

    except ValueError as e:
        logger.warning("Agent error: %s", e)
        raise HTTPException(
            status_code=400,
            detail="Unable to process the requested operation"
        ) from e

    except RuntimeError as e:
        logger.error("Agent runtime error: %s", e)
        raise HTTPException(
            status_code=503,
            detail="Agent could not complete the request"
        ) from e

    except Exception:
        logger.exception("Unexpected failure")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
