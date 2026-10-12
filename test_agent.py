from config import LLM_MODEL, HF_TOKEN

from src.llm.client import LLMClient
from src.llm.prompts import TOOL_SYSTEM_PROMPT
from src.agent.agent import Agent


def main():

    llm = LLMClient(
        LLM_MODEL,
        hf_token=HF_TOKEN
    )

    agent = Agent(
        llm=llm,
        max_iterations=5
    )

    messages = [
        {
            "role": "system",
            "content": TOOL_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": (
                "What is 847 multiplied by 392? Use the calculator."
            )
        }
    ]

    answer = agent.run(messages)

    print("\nFINAL ANSWER:")
    print(answer)


if __name__ == "__main__":
    main()