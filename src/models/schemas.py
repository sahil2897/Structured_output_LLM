from pydantic import BaseModel, Field
from typing import Any

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


class ToolCall(BaseModel):
    name: str = Field(
        ...,
        description="Name of the tool to execute"
    )

    arguments: dict[str, Any] = Field(
        ...,
        description="Arguments to pass to the tool"
    )


class CalculatorInput(BaseModel):
    expression: str = Field(
        ...,
        min_length=1,
        description=(
            "Mathematical expression to evaluate, "
            "for example '3847 * 927'"
        )
    )

