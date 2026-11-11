from ollama import AsyncClient
from tools import AVAILABLE_TOOLS, TOOL_MAP

class AsyncOllamaAgent:
    def __init__(self, model_name: str, temperature: float, num_ctx: int):
        self.model_name = model_name
        self.options = {"temperature": temperature, "num_ctx": num_ctx}
        self.client = AsyncClient()

    async def run_agent_loop(self, messages: list, max_turns: int = 5):
        """
        Executes a multi-turn agentic loop allowing repeated tool calls until completion.
        """
        current_messages = list(messages)
        
        for _ in range(max_turns):
            response = await self.client.chat(
                model=self.model_name,
                messages=current_messages,
                tools=AVAILABLE_TOOLS,
                options=self.options
            )

            msg = response["message"]
            tool_calls = msg.get("tool_calls")

            # If no tool calls requested, return final response
            if not tool_calls:
                return msg["content"], current_messages

            # Append assistant message requesting tool execution
            current_messages.append(msg)

            # Process tool calls
            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                args = tool_call["function"].get("arguments", {})

                if func_name in TOOL_MAP:
                    try:
                        # Execute async tool
                        result = await TOOL_MAP[func_name](**args)
                    except Exception as err:
                        result = f"Error executing {func_name}: {err}"

                    current_messages.append({
                        "role": "tool",
                        "content": str(result),
                        "name": func_name
                    })

        return "Agent reached maximum tool invocation limits.", current_messages