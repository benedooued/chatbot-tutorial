Version 4 limitations


Limitation 1: Naive Sliding Window Context Loss
The Flaw: In memory.py, trimming history by message count ([-max_history:]) drops older messages indiscriminately.

Concrete Example:

Turn 1 (User): "My name is Ariel and I am writing a paper on IoT anomaly detection."

Turns 2 to 12: You ask several general Python and tool-usage questions.

Turn 13 (User): "What was my name and topic again?"

Result: Message #1 was pushed past the max_history=12 window and dropped. The model gives a hallucinated or empty response because key facts were discarded during context truncation.


Limitation 2: Loss of Non-Text Streaming Details
The Flaw: In client.py, calling await client.chat(...) without streaming waits for the entire inference step to complete before outputting text. If a response takes 8 seconds, the terminal displays nothing until the end. Conversely, if you stream raw text, token counts, execution metrics, and intermediate tool call metadata are lost.

Concrete Example:

When executing calculate_expression("125 * 80"), the UI shows a generic "Thinking..." indicator. The user gets zero visibility into which tool was selected, what arguments were passed, or whether the model is looping or frozen.





Limitation 4: Fixed Model Hardware Parameters
The Flaw: Model execution parameters like token generation limits (num_predict), memory retention duration (keep_alive), and custom system prompts are hardcoded into Python files.

Concrete Example:

If the model gets stuck in an infinite output loop, there is no max token limit configured via num_predict to cut off generation. Furthermore, every request defaults Ollama's model unloading timer (keep_alive) to standard settings rather than keeping it pinned in GPU VRAM.


Solutions

2. What We Are Adding in Version 5



In-Memory Semantic Summarization: When context length exceeds N messages, the system automatically runs a lightweight background call to summarize older turns into a single "summary" block, maintaining long-term memory alongside recent chat turns.


Streamed UI with Real-time Tool Telemetry: Render tool invocations, argument parsing, and streamed response tokens directly in terminal panels using rich.live.

Hardware & Token Production Controls: Pass num_predict and keep_alive directly into Ollama API options for precise control over VRAM retention and response caps.