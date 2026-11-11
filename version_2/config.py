from dataclasses import dataclass

@dataclass
class Config:
    model_name: str = "qwen3.5:4b"
    system_prompt: str = "You are a helpful, concise AI assistant."
    max_history_messages: int = 10  # Maximum history turns retained (excluding system prompt)