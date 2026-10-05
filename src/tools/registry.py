from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel

from src.models.schemas import CalculatorInput
from src.tools.calculator import calculator


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_model: type[BaseModel]
    function: Callable

    def to_llm_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_model.model_json_schema()
            }
        }


CALCULATOR = ToolDefinition(
    name="calculator",
    description=(
        "Evaluate a mathematical expression. "
        "Use this tool when accurate arithmetic is required."
    ),
    input_model=CalculatorInput,
    function=calculator
)


TOOL_REGISTRY = {
    CALCULATOR.name: CALCULATOR
}


TOOLS = [
    tool.to_llm_schema()
    for tool in TOOL_REGISTRY.values()
]


