from config import Config
from memory import ConversationMemory
from client import OllamaClient




def main():
    cfg = Config()
    memory = ConversationMemory(system_prompt=cfg.system_prompt, max_history=cfg.max_history_messages)
    client = OllamaClient(model_name=cfg.model_name)

    print(f"--- Chatbot v2 [{cfg.model_name}] ---")
    print("Commands: 'exit' to quit, 'clear' to reset memory.\n")

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
            print("System: Memory cleared.\n")
            continue

        memory.add_message("user", user_input)
        print("Assistant: ", end="", flush=True)

        full_response = ""
        try:
            for chunk in client.stream_chat(memory.get_context()):
                print(chunk, end="", flush=True)
                full_response += chunk
            print("\n")
            
            # Save response only upon successful stream completion
            memory.add_message("assistant", full_response)

        except Exception as e:
            print(f"\n[Error]: Failed to retrieve response: {e}\n")

if __name__ == "__main__":
    main()