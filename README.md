
# LLM Application Engineering — Week 3

A production-oriented LLM API built using FastAPI, AsyncOpenAI, and vLLM.

## Architecture

```text
Client (curl / httpx)
        |
        v
FastAPI (Port 8000)
        |
        |-- Request validation (Pydantic)
        |-- Error handling
        |-- Timeouts and retries (/chat)
        |-- Structured logging (/chat)
        |-- Token streaming (/chat/stream)
        |
        v
AsyncOpenAI SDK
        |
        v
vLLM (Port 8001)
        |
        v
Qwen/Qwen3-1.7B
```

## Technology Stack

- Python 3.12
- FastAPI + Uvicorn
- OpenAI Python SDK (AsyncOpenAI)
- vLLM
- Qwen/Qwen3-1.7B
- Pydantic
- httpx
- structlog
- pytest

Inference hardware: Apple M1 Pro.

## Features

### Structured Outputs and Agents
- Pydantic response validation
- Structured-output repair
- Tool calling
- Tool registry and multi-step agent execution

### API and Concurrency
- FastAPI endpoints
- Async request handling
- Shared inference client using application lifespan
- Concurrent inference using vLLM

### Reliability
- Configurable inference timeouts
- Retries for transient failures
- Exponential backoff with jitter
- HTTP error mapping
- Structured JSON logging with request IDs on /chat

### Streaming
- Asynchronous token streaming
- FastAPI StreamingResponse
- Client cancellation handling
- Midstream error handling
- Upstream stream cleanup

## Running the Application

### 1. Start vLLM

Start the existing working vLLM server using:

- Model: Qwen/Qwen3-1.7B
- Host: 127.0.0.1
- Port: 8001

Use the startup command configured for the M1 Pro environment.

### 2. Start FastAPI

From the project root:

```bash
uvicorn src.api.vllm_main:app --port 8000
```

### 3. Standard Chat API

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain RAG in one sentence."}'
```

Returns a complete JSON response.

### 4. Streaming Chat API

```bash
curl -N -X POST http://127.0.0.1:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain attention in transformers."}'
```

Returns generated text progressively.

## Testing

Run automated tests:

```bash
python -m pytest tests/ -v
```

Test coverage includes:
- Successful inference
- Invalid request validation
- Upstream connection failures
- Timeout handling
- Retry behavior
- Streaming responses
- Midstream failures
- Resource cleanup

## Concurrent Streaming

The application has been exercised with five concurrent streaming requests using httpx.AsyncClient.

Measurements:
- Time to first text chunk (TTFT approximation)
- Total request latency
- Total wall time
- Response size

Actual performance depends on the inference configuration and hardware.

## Current Limitations

- Streaming responses use plain text rather than structured SSE events.
- The streaming endpoint does not currently use the /chat retry mechanism.
- Stream cancellation and error handling can be expanded.
- Authentication, rate limiting, and production deployment configuration are not included.

## Future Improvements

- Structured Server-Sent Events (SSE)
- Request tracing across services
- Load testing and latency metrics
- Prometheus/OpenTelemetry instrumentation
- Containerization and deployment
- Production observability and evaluation
