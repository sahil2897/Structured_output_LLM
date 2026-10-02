from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="User's message"
    )


class AssistantResponse(BaseModel):
    answer: str = Field(
        ...,
        description="The answer to the user's question"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1"
    )


