import ollama

class OllamaClient:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def stream_chat(self, messages: list):
        """Yields content chunks from Ollama API."""
        response = ollama.chat(
            model=self.model_name,
            messages=messages,
            stream=True
        )
        for chunk in response:
            yield chunk["message"]["content"]