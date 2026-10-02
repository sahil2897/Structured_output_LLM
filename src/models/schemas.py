from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User's message"
    )


class AssistantResponse(BaseModel):
    answer: str
    confidence: float = Field(
        ge=0.0,
        le=1.0
    )


