Version 3 :


Synchronous/Blocking Tool Execution: Calling a tool stops execution completely while waiting for the tool function to finish.
When the Python interpreter hits a function call, execution halts completely until that function finishes and returns a value. Your program cannot do any other work during this time.
If your tool fetches a web page, queries a database, or computes a complex operation taking 5 seconds, your whole application freezes for 5 seconds.
If the model returns 3 tool calls in message["tool_calls"], your for loop executes them one after another (Tool 1 → wait → Tool 2 → wait → Tool 3 → wait), instead of running all 3 simultaneously in parallel.


Fragile Tool Call Handling: The single-pass chat_step logic fails if the model makes multiple tool calls in sequence or if a tool returns an error. If the model requests 2 or more tools at once (e.g., ["get_weather", "get_time"]), your loop breaks on the first iteration. Because of the return statement inside the loop, only the first tool is ever executed. The remaining tool calls requested by the model are ignored entirely.

Naive File Storage: Storing history as a raw json array writes the whole file to disk on every message. It lacks metadata


Lack of Model-Driven System Prompt Flexibility: The system prompt is hardcoded at startup; users cannot dynamically adjust system behavior or parameters mid-session.

No tool error handling

What we are going to add for version 4:

Asynchronous Tool Execution: Implement async

Session & Metadata Management: Support multi-session history tagged with session_id and timestamps.

Resilient Multi-Step Agentic Loop: Allow the assistant to execute tools recursively in a loop until it produces a final response.


Asynchronous Execution (asyncio): Non-blocking API requests and tool evaluation.

Rich CLI Formatting: Clean terminal display showing tool execution states using rich.
