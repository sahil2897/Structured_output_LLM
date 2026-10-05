from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel

from src.models.schemas import CalculatorInput
from src.tools.calculator_tool import calculator

from src.models.schemas import CurrentDateTimeInput
from src.tools.datetime_tool import get_current_datetime

from src.models.schemas import ExchangeRateInput
from src.tools.exchange_rate import get_exchange_rate


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

CURRENT_DATETIME = ToolDefinition(
    name="get_current_datetime",
    description=(
        "Get the current local date and time.",
        "Use this tool when user asks for the current date or time"
    ),
    input_model=CurrentDateTimeInput,
    function=get_current_datetime
)

EXCHANGE_RATE = ToolDefinition(
    name="get_exchange_rate",
    description=(
        "Get the exchange rate between two currencies. "
        "Use three-letter currency codes such as USD, EUR, or INR."
    ),
    input_model=ExchangeRateInput,
    function=get_exchange_rate
)


TOOL_REGISTRY = {
    CALCULATOR.name: CALCULATOR,
    CURRENT_DATETIME.name:CURRENT_DATETIME,
    EXCHANGE_RATE.name:EXCHANGE_RATE
}


TOOLS = [
    tool.to_llm_schema()
    for tool in TOOL_REGISTRY.values()
]


