import json

from src.models.schemas import ToolCall


def parse_tool_call(raw_output: str) -> ToolCall:

    cleaned = raw_output.strip()

    if not (
        cleaned.startswith("<tool_call>")
        and cleaned.endswith("</tool_call>")
    ):
        raise ValueError(
            "LLM response is not a tool call"
        )

    cleaned = cleaned.removeprefix(
        "<tool_call>"
    )

    cleaned = cleaned.removesuffix(
        "</tool_call>"
    )

    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid tool call JSON: {error}"
        ) from error

    return ToolCall.model_validate(data)