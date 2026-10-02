import json

from config import LLM_MODEL, HF_TOKEN
from src.llm.client import LLMClient
from src.llm.prompts import SYSTEM_PROMPT
from src.llm.parser import StructuredOutputParser
from src.llm.structured import StructuredLLM
from src.models.schemas import AssistantResponse



def main():

    llm = LLMClient(LLM_MODEL,hf_token=HF_TOKEN)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": "What is the difference between a CNN and an RNN?"
        }
    ]

    structured_llm = StructuredLLM(
        llm=llm,
        schema=AssistantResponse,
        max_retries=5
    )

    response = structured_llm.generate(messages)

    print("\nVALIDATED RESPONSE:")
    print(response)

    print("\nANSWER:")
    print(response.answer)

    print("\nCONFIDENCE:")
    print(response.confidence)


if __name__ == "__main__":
    main()