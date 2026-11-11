from ollama import AsyncClient

class PreferenceAgent:
    def __init__(self, model_name: str, temperature: float, num_ctx: int, num_predict: int, keep_alive: str):
        self.model_name = model_name
        self.keep_alive = keep_alive
        self.options = {
            "temperature": temperature,
            "num_ctx": num_ctx,
            "num_predict": num_predict
        }
        self.client = AsyncClient()

    async def generate_response(self, messages: list) -> str:
        response = await self.client.chat(
            model=self.model_name,
            messages=messages,
            options=self.options,
            keep_alive=self.keep_alive
        )
        return response["message"]["content"]