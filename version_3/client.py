import ollama
from tools import AVAILABLE_TOOLS, TOOL_MAP

class OllamaClient:
    def __init__(self, model_name: str, temperature: float, num_ctx: int):
        self.model_name = model_name
        self.options = {
            "temperature": temperature,
            "num_ctx": num_ctx
        }

    def chat_step(self, messages: list):
        """
        Sends context to Ollama, inspects if the model requested a tool call,
        executes it locally if necessary, and returns the generated content.
        """
        response = ollama.chat(
            model=self.model_name,
            messages=messages,
            tools=AVAILABLE_TOOLS,
            options=self.options
        )

        message = response["message"]

        # If model decides to call a function/tool
        if message.get("tool_calls"):
            for tool_call in message["tool_calls"]:
                func_name = tool_call["function"]["name"]
                args = tool_call["function"].get("arguments", {})

                if func_name in TOOL_MAP:
                    # Execute tool locally
                    # Execution freezes here until the Python tool function finishes
                    result = TOOL_MAP[func_name](**args)

                    # Append tool response back into the conversation context
                    messages.append(message)
                    messages.append({
                        "role": "tool",
                        "content": str(result),
                        "name": func_name
                    })

                    # Follow up call to complete the answer using tool output
                    follow_up = ollama.chat(
                        model=self.model_name,
                        messages=messages,
                        options=self.options
                    )
                    return follow_up["message"]["content"]

        return message["content"]