import asyncio

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from openai import APIConnectionError, APIStatusError
from src.api.vllm_main import generate_with_retry


REQUEST_URL = "http://127.0.0.1:8001/v1/chat/completions"


def test_retry_then_success():

    request = httpx.Request("POST", REQUEST_URL)

    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="Hello!")
            )
        ]
    )

    client = MagicMock()

    # First two calls fail, third succeeds
    client.chat.completions.create = AsyncMock(
        side_effect=[
            APIConnectionError(request=request),
            APIConnectionError(request=request),
            fake_response,
        ]
    )

    # Eliminate waiting during the test
    with patch(
        "src.api.vllm_main.random.uniform",
        return_value=0.0
    ):
        result = asyncio.run(
            generate_with_retry(
                client,
                [{"role": "user", "content": "Hello"}]
            )
        )

    assert result is fake_response
    assert client.chat.completions.create.await_count == 3


def test_non_retryable_error():

    request = httpx.Request("POST", REQUEST_URL)

    error = APIStatusError(
        "Bad request",
        response=httpx.Response(400, request=request),
        body=None
    )

    client = MagicMock()
    client.chat.completions.create = AsyncMock(
        side_effect=error
    )

    with pytest.raises(APIStatusError):
        asyncio.run(
            generate_with_retry(
                client,
                [{"role": "user", "content": "Hello"}]
            )
        )

    # HTTP 400 must NOT trigger retries
    assert client.chat.completions.create.await_count == 1