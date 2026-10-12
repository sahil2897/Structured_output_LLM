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


TOOL_SYSTEM_PROMPT = """
You are a helpful AI assistant with access to external tools.

Instructions:
- Use tools when they are necessary to answer the user's question.
- Do not call tools unnecessarily.
- Never invent or fabricate tool results.
- When a tool returns a result, use it to continue solving the user's request.
- If additional tools are needed, call them.
- Once you have enough information, provide a clear final answer.
- Do not invent tools that are not available.
"""