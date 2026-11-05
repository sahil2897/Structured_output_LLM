from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from src.api.vllm_main import app

import httpx
from openai import APITimeoutError, APIConnectionError


def test_chat_success():

    # Simulate a successful LLM response
    fake_response = SimpleNamespace(
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="Paris")
            )
        ],
        usage=SimpleNamespace(
            prompt_tokens=12,
            completion_tokens=5
        )
    )

    # Replace the real inference function
    with patch(
        "src.api.vllm_main.generate_with_retry",
        new_callable=AsyncMock
    ) as mock_generate:

        mock_generate.return_value = fake_response

        with TestClient(app) as client:

            response = client.post(
                "/chat",
                json={"message": "What is the capital of France?"}
            )

    assert response.status_code == 200
    assert response.json() == {"answer": "Paris"}
    
    mock_generate.assert_awaited_once()


def test_chat_invalid_request():

    with TestClient(app) as client:

        response = client.post(
            "/chat",
            json={"message": ""}
        )

    assert response.status_code == 422


def test_chat_timeout():

    fake_request = httpx.Request(
        "POST",
        "http://127.0.0.1:8001/v1/chat/completions"
    )

    with patch(
        "src.api.vllm_main.generate_with_retry",
        new_callable=AsyncMock
    ) as mock_generate:

        mock_generate.side_effect = APITimeoutError(
            request=fake_request
        )

        with TestClient(app) as client:
            response = client.post(
                "/chat",
                json={"message": "Hello"}
            )

    assert response.status_code == 504
    assert response.json()["detail"] == "Inference server timed out"


def test_chat_connection_error():

    fake_request = httpx.Request(
        "POST",
        "http://127.0.0.1:8001/v1/chat/completions"
    )

    with patch(
        "src.api.vllm_main.generate_with_retry",
        new_callable=AsyncMock
    ) as mock_generate:

        mock_generate.side_effect = APIConnectionError(
            request=fake_request
        )

        with TestClient(app) as client:
            response = client.post(
                "/chat",
                json={"message": "Hello"}
            )

    assert response.status_code == 503
    assert response.json()["detail"] == "Inference server unavailable"