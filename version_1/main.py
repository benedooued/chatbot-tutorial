import ollama




def run_chatbot():
    # 1. Initialize conversation state with a system role defining behavior
    messages = [
        {
            "role": "system",
            "content": "You are a helpful, concise AI assistant."
        }
    ]

    MODEL_NAME = "qwen3.5:4b"
    
    print(f"--- Chatbot initialized with model: {MODEL_NAME} ---")
    
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        # 2. Get user input
        user_input = input("You: ").strip()

        # Handle exit condition
        if user_input.lower() in ["exit", "quit"]:
            print("Ending session.")
            break

        if not user_input:
            continue

        # 3. Append user message to history
        messages.append({"role": "user", "content": user_input})

        print("Assistant: ", end="", flush=True)

        try:
            # 4. Stream response from Ollama API
            response_stream = ollama.chat(
                model=MODEL_NAME,
                messages=messages,
                stream=True
            )
            
            print(response_stream)

            full_response = ""
            for chunk in response_stream:
                content = chunk["message"]["content"]
                print(content, end="", flush=True)
                full_response += content

            print("\n")

            # 5. Save assistant response back to history to maintain context
            messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            print(f"\nError interacting with Ollama: {e}\n")

if __name__ == "__main__":
    run_chatbot()