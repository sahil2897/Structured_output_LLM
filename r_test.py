from config import LLM_MODEL, HF_TOKEN

from src.llm.client import LLMClient
from src.tools.registry import CALCULATOR_TOOL
from src.llm.tool_parser import parse_tool_call

from src.models.schemas import CalculatorInput
from src.tools.calculator import calculator


def main():

    llm = LLMClient(
        LLM_MODEL,
        hf_token=HF_TOKEN
    )

    messages = [
        {
            "role": "user",
            "content": (
                "I love the book 1984 and I read it 2 times, can you tell me who wrote it?"
            )
        }
    ]

    response = llm.generate(
        messages,
        tools=[CALCULATOR_TOOL]
    )

    print("\nRAW MODEL RESPONSE:")
    print(response)

    tool_call = parse_tool_call(response)

    print("\nPARSED TOOL CALL:")
    print(tool_call)

    print("\nTOOL NAME:")
    print(tool_call.name)

    print("\nTOOL ARGUMENTS:")
    print(tool_call.arguments)

    if tool_call.name == "calculator":

        calculator_input = CalculatorInput.model_validate(
            tool_call.arguments
        )

        print("\nVALIDATED CALCULATOR INPUT:")
        print(calculator_input)

        result = calculator(
            calculator_input.expression
        )

        print("\nTOOL RESULT:")
        print(result)

        messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

        messages.append(
                {
                    "role": "tool",
                    "name": tool_call.name,
                    "content": str(result)
                }
            )

        final_response = llm.generate(
                messages,
                tools=[CALCULATOR_TOOL]
            )

        print("\nFINAL RESPONSE:")
        print(final_response)



if __name__ == "__main__":
    main()