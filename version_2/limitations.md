Version 2

Information Loss (Simple Truncation): Dropping older messages blindly can cause the model to lose key details established earlier in the chat

Lack of Generation Control: Standard temperature and top-p settings are unconfigured, meaning deterministic output or custom context limits (num_ctx) aren't enforced.

No External Capabilities: The bot is limited strictly to internal parametric knowledge and cannot fetch live data or invoke code/tools.

No Session Persistence: History resets every time the script exits; conversation states are lost across runs.

In version 3, we are going to add:
Model Generation Options: Expose generation hyper-parameters

Function/Tool Calling: Enable qwen3.5:4b to trigger Python tools

File Persistence: Automatically load and save conversation history to a local JSON file across runs.

Smart Memory Truncation: Keep the original system prompt intact while saving/loading previous sessions safely.
