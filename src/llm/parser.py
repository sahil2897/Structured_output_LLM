import json
from typing import Type, TypeVar

from pydantic import BaseModel, ValidationError


T = TypeVar("T", bound=BaseModel)


class StructuredOutputParser:
    def __init__(self, schema: Type[T]):
        self.schema = schema

    def parse(self, raw_output: str) -> T:
        cleaned_output = self._clean_markdown(raw_output)

        try:
            data = json.loads(cleaned_output)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Invalid JSON returned by LLM: {e}"
            ) from e

        try:
            return self.schema.model_validate(data)

        except ValidationError as e:
            raise ValueError(
                f"LLM output failed schema validation:\n{e}"
            ) from e

    def _clean_markdown(self, text: str) -> str:
        text = text.strip()

        if text.startswith("```json"):
            text = text[len("```json"):]

        elif text.startswith("```"):
            text = text[len("```"):]

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()