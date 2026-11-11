from dataclasses import dataclass, field

@dataclass
class Config:
    model_name: str = "qwen3.5:4b"
    system_prompt: str = "You are a helpful assistant capable of using tools when necessary."
    max_history_messages: int = 10
    storage_file: str = "version_3/chat_history.json"
    temperature: float = 0.7
    num_ctx: int = 4096