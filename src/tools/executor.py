from typing import Any

from src.models.schemas import ToolCall
from src.tools.registry import TOOL_REGISTRY


def execute_tool(tool_call: ToolCall) -> Any:

    if tool_call.name not in TOOL_REGISTRY:
        raise ValueError(
            f"Unknown tool: {tool_call.name}"
        )

    tool = TOOL_REGISTRY[tool_call.name]

    validated_input = tool.input_model.model_validate(
        tool_call.arguments
    )

    result = tool.function(
        **validated_input.model_dump()
    )

    return result