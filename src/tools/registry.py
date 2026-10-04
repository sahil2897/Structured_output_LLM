from src.models.schemas import CalculatorInput


CALCULATOR_TOOL = {
    "type": "function",
    "function": {
        "name": "calculator",
        "description": (
            "Evaluate a mathematical expression. "
            "Use this tool when accurate arithmetic is required."
        ),
        "parameters": CalculatorInput.model_json_schema()
    }
}