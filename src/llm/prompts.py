import json
from pydantic import BaseModel

def build_system_prompt(schema: type[BaseModel]) -> str:
    json_schema = schema.model_json_schema()

    schema_text = json.dumps(json_schema,indent=2)

    
    SYSTEM_PROMPT = f"""
        You are an AI assistant.

        You MUST respond with valid JSON that conforms exactly
        to the following JSON Schema:

        {schema_text}

        Rules:

        - Follow the JSON Schema exactly.
        - Do not add fields that are not defined in the schema.
        - Do not use markdown.
        - Do not include explanations outside the JSON.
        - Do not wrap the JSON in ```json blocks.
        """

    return SYSTEM_PROMPT