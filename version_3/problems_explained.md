Synchronous / Blocking Tool Execution
What it means
In synchronous code, Python executes instructions sequentially line by line. When a line calls a tool (like downloading a file or querying an external database), Python pauses execution on that exact line. Nothing else can happen in your program until that tool returns a result.

Example Problem
Suppose a user asks: "Check the weather in Paris, then calculate 15 * 4."

The Async Fix (Version 4)
With async/await, Python can pause a task while waiting for an HTTP call to finish, returning control to the main event loop to keep the user interface alive or handle parallel background tasks.


2. Naive File Storage
What it means
A standard .json file contains a single, strictly formatted JSON array: [ {...}, {...} ]. You cannot simply "append" a line to a JSON array on disk without overwriting the closing bracket ].

This causes two major issues:

Performance Overhead: To save a new message, you must open the entire file, load all 10,000 previous messages into memory, insert 1 new message, parse it into a JSON string, and write the whole file back to disk.

Missing Metadata: A simple array [{"role": "user", "content": "hi"}] doesn't track who said it, when it was said, or which conversation session it belongs to.


Example Scenario
Imagine a JSON file growing over months:

JSON
// Version 3 raw JSON array (chat_history.json)
[
  {"role": "user", "content": "Hi, I am Alex."},
  {"role": "assistant", "content": "Hello Alex!"}
]
What goes wrong:

No multi-user / session support: If you run two chatbot terminal windows at the same time, both read and overwrite chat_history.json, corrupting each other's memory.

No Analytics: You cannot sort messages by date or know when the user last spoke.


The Fix (Version 4)
We wrapped messages in structured JSON with metadata and generated unique session_ids stored in dedicated files (sessions/session_<id>.json):

JSON
// Version 4 Structured File Storage
{
  "session_id": "a1b2c3d4",
  "updated_at": "2026-03-30T10:15:30",
  "messages": [
    {
      "role": "user",
      "content": "Hi, I am Alex.",
      "timestamp": "2026-03-30T10:15:28"
    }
  ]
}


3. Fragile Tool Call Handling
What it means
In Version 3, client.py only checked for tool calls once (if message.get("tool_calls"): ...).

Large Language Models (LLMs) often need to execute tools in chain reaction loops:

Multiple tools sequentially: Tool A output is needed to decide args for Tool B.

Tool Failure / Recovery: A tool throws an exception, and the LLM needs to see the error message so it can correct its input parameters and try again.

Example Scenario
User asks: "What is the weather in Paris, and what is 500 divided by the temperature number?"

Pass 1: Model decides to call get_weather("Paris").

Tool Output: Returns "Sunny, 20°C".

Pass 2 (Requires another tool): Model reads 20 and now needs to call calculate_expression("500 / 20").

Why Version 3 Failed:
In Version 3, after executing Pass 1, the code returned the response immediately. It never checked if the model wanted to execute a second tool (calculate_expression) after receiving the weather data.


The Fix (Version 4)
We implemented a while/for loop agentic control flow (run_agent_loop):

Python
# Version 4 agentic loop concept
for turn in range(max_turns):
    response = await client.chat(...)
    if not response.tool_calls:
        return response.content  # Exit loop only when LLM is done asking for tools
    
    # Execute tools, add outputs back to message history, and continue loop!



4. Lack of Model-Driven System Prompt Flexibility
What it means
In Version 1–3, the system prompt was defined statically when initializing the application (system_prompt = "You are a helpful assistant").

If a user wanted to change the chatbot's role mid-conversation (e.g., "Act as a strict Senior Python Code Reviewer from now on"), the chatbot could get confused because the underlying application kept re-injecting the original hardcoded system prompt at the top of every context window payload.

Example Scenario
Python
# Hardcoded System Prompt in Version 2/3
def get_context():
    return [{"role": "system", "content": "You are a concise assistant."}] + history

# User types in chat:
# "Please talk to me like a pirate from now on."

# Payload sent to Ollama API:
[
  {"role": "system", "content": "You are a concise assistant."},  # <-- Hardcoded instruction conflicts!
  {"role": "user", "content": "Please talk to me like a pirate from now on."},
  {"role": "assistant", "content": "Aye aye matey!"},
  {"role": "user", "content": "What is Python?"}
]
The model receives two conflicting instructions: the hardcoded system prompt asking for concise normal responses and the user prompt asking for pirate speech. Over time, the hardcoded system prompt wins out and overrides the user's intent.


How to Address This in Future Refactoring
To allow dynamic prompt changes mid-session, you can:

Allow updating memory.system_prompt dynamically via slash commands (e.g., /system You are a pirate).

Alternatively, let user instructions append directly to the conversation history while keeping the system prompt as a general baseline rule rather than a rigid behavioral constraint.