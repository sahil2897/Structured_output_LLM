from src.llm.tool_parser import parse_tool_call, is_tool_call
from src.tools.executor import execute_tool
from src.tools.registry import TOOLS


class Agent:

    def __init__(
        self,
        llm,
        max_iterations: int = 5
    ):
        self.llm = llm
        self.max_iterations = max_iterations

    def run(self, messages):

        for iteration in range(self.max_iterations):

            print(
                f"\nAgent iteration "
                f"{iteration + 1}/{self.max_iterations}"
            )

            response = self.llm.generate(
                messages,
                tools=TOOLS
            )
            
            print("\nMODEL RESPONSE:")
            print(response)

            if not is_tool_call(response):
                return response
            
            tool_call = parse_tool_call(response)

            result = execute_tool(tool_call)

            print("\nTOOL RESULT:")
            print(result)

            messages.append({
                    "role": "assistant",
                    "content": response
                    })

            messages.append({
                    "role": "tool",
                    "name": tool_call.name,
                    "content": str(result)
                    })