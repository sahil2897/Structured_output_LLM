import json
from src.models.schemas import AssistantResponse

print(
    json.dumps(
        AssistantResponse.model_json_schema(),
        indent=2
    )
)