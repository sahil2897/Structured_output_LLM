from pydantic import BaseModel

from src.llm.parser import StructuredOutputParser

from pprint import pprint

class StructuredLLM:

    def __init__(
        self,
        llm,
        schema: type[BaseModel],
        max_retries: int = 2
    ):
        self.llm = llm
        self.parser = StructuredOutputParser(schema)
        self.max_retries = max_retries

    def generate(self, messages):

        current_messages = list(messages)

        for attempt in range(self.max_retries + 1):

            print(
                f"\nAttempt {attempt + 1}/"
                f"{self.max_retries + 1}"
            )

            raw_output = self.llm.generate(current_messages)

            try:
                response = self.parser.parse(raw_output)

                print("Structured output validation: SUCCESS")

                return response

            except ValueError as error:

                print("Structured output validation: FAILED")
                print(f"Error: {error}")

                # No retries remaining
                # if attempt == self.max_retries:
                #     raise

                # Give the LLM both:
                # 1. Its previous output
                # 2. The validation error
                retry_message = {
                    "role": "user",
                    "content": (
                        "Your previous response was:\n\n"
                        f"{raw_output}\n\n"
                        "The response failed schema validation "
                        "with the following error:\n\n"
                        f"{error}\n\n"
                        "Correct your previous response based on "
                        "this error.\n"
                        "Return ONLY valid JSON matching the "
                        "required schema."
                    )
                }

                current_messages.append(retry_message)

        pprint(f"Final messages for LLM: {current_messages}")
