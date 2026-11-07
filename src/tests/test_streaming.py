from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
from fastapi.testclient import TestClient
from openai import APIConnectionError

from src.api.vllm_main import app


# Fake asynchronous stream
class FakeStream:
    def __init__(self, texts):
        self.texts = iter(texts)
        self.closed = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            text = next(self.texts)
        except StopIteration:
            raise StopAsyncIteration

        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    delta=SimpleNamespace(content=text)
                )
            ]
        )

    async def close(self):
        self.closed = True


def test_streaming_success():

    fake_stream = FakeStream([
        "Hello",
        " from",
        " Qwen!"
    ])

    fake_client = MagicMock()
    fake_client.chat.completions.create = AsyncMock(
        return_value=fake_stream
    )
    fake_client.close = AsyncMock()

    with patch(
        "src.api.vllm_main.AsyncOpenAI",
        return_value=fake_client
    ):
        with TestClient(app) as client:
            response = client.post(
                "/chat/stream",
                json={"message": "Say hello"}
            )

    assert response.status_code == 200
    assert response.text == "Hello from Qwen!"
    assert fake_stream.closed
    fake_client.chat.completions.create.assert_awaited_once()


def test_streaming_connection_error():

    fake_request = httpx.Request(
        "POST",
        "http://127.0.0.1:8001/v1/chat/completions"
    )

    fake_client = MagicMock()
    fake_client.chat.completions.create = AsyncMock(
        side_effect=APIConnectionError(
            request=fake_request
        )
    )
    fake_client.close = AsyncMock()

    with patch(
        "src.api.vllm_main.AsyncOpenAI",
        return_value=fake_client
    ):
        with TestClient(app) as client:
            response = client.post(
                "/chat/stream",
                json={"message": "Hello"}
            )

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Inference server unavailable"
    }


class FailingStream(FakeStream):

    async def __anext__(self):
        try:
            return await super().__anext__()

        except StopAsyncIteration:
            raise RuntimeError("Simulated stream failure")


def test_streaming_midstream_failure():

    fake_stream = FailingStream(["Hello"])

    fake_client = MagicMock()
    fake_client.chat.completions.create = AsyncMock(
        return_value=fake_stream
    )
    fake_client.close = AsyncMock()

    with patch(
        "src.api.vllm_main.AsyncOpenAI",
        return_value=fake_client
    ):
        with TestClient(app) as client:
            response = client.post(
                "/chat/stream",
                json={"message": "Say hello"}
            )

    assert response.status_code == 200

    assert response.text == (
        "Hello\n[Stream interrupted. Please retry.]\n"
    )

    assert fake_stream.closed is True