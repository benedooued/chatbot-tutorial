from ollama import AsyncClient
from tools import AVAILABLE_TOOLS, TOOL_MAP

class TelemetryOllamaAgent:
    def __init__(self, model_name: str, temperature: float, num_ctx: int, num_predict: int, keep_alive: str):
        self.model_name = model_name
        self.keep_alive = keep_alive
        self.options = {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": num_predict
        }
        self.client = AsyncClient()

    async def run_agent_loop(self, messages: list, telemetry_callback=None, max_turns: int = 5):
        current_messages = list(messages)
        
        for _ in range(max_turns):
            response = await self.client.chat(
                model=self.model_name,
                messages=current_messages,
                tools=AVAILABLE_TOOLS,
                options=self.options,
                keep_alive=self.keep_alive
            )

            msg = response["message"]
            tool_calls = msg.get("tool_calls")

            if not tool_calls:
                return msg["content"], current_messages

            current_messages.append(msg)

            for tool_call in tool_calls:
                func_name = tool_call["function"]["name"]
                args = tool_call["function"].get("arguments", {})

                if telemetry_callback:
                    await telemetry_callback(f"[bold yellow]Executing Tool:[/bold yellow] {func_name}({args})")

                if func_name in TOOL_MAP:
                    try:
                        result = await TOOL_MAP[func_name](**args)
                    except Exception as err:
                        result = f"Error executing {func_name}: {err}"

                    current_messages.append({
                        "role": "tool",
                        "content": str(result),
                        "name": func_name
                    })

        return "Agent reached maximum tool execution depth.", current_messages