from config import Config
from memory import ConversationMemory
from client import OllamaClient



def main():
    cfg = Config()
    memory = ConversationMemory(
        system_prompt=cfg.system_prompt,
        max_history=cfg.max_history_messages,
        storage_file=cfg.storage_file
    )
    client = OllamaClient(
        model_name=cfg.model_name,
        temperature=cfg.temperature,
        num_ctx=cfg.num_ctx
    )

    print(f"--- Chatbot v3 [{cfg.model_name}] ---")
    print("Commands: 'exit' to quit, 'clear' to reset history.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            break

        if user_input.lower() == "clear":
            memory.clear()
            print("System: History cleared and storage wiped.\n")
            continue

        memory.add_message("user", user_input)

        try:
            response_text = client.chat_step(memory.get_context())
            print(f"Assistant: {response_text}\n")
            memory.add_message("assistant", response_text)
        except Exception as e:
            print(f"\n[Error]: {e}\n")

if __name__ == "__main__":
    main()