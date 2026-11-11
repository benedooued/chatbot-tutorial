Event Loop Blocking via Synchronous Ollama Call

Calling ollama.chat() inside the async summarize_if_needed() function blocks the entire main execution thread during memory compression.

Example: While compressing context, user inputs freeze and telemetry logging halts until Ollama finishes generating the summary.

Hard Truncation & Lack of Pagination in File Reading

The read_local_file function reads only the first 2,000 characters using f.read(2000).

Example: If a document is 10,000 characters long, the agent cannot access content past character 2000 because it lacks pagination parameters like offset or line_number.

Naïve Summary String Concatenation

New summaries are appended directly onto old ones using string formatting (self.summary += f"\n{new_summary_text}").

Example: Over a long conversation, self.summary grows endlessly with duplicate points, eventually exceeding the model's context window (num_ctx).


Sequential Execution of Async Tools

Inside run_agent_loop, multiple tool calls are awaited inside a standard for loop instead of being run concurrently.

Example: If the model requests 3 tool calls taking 2 seconds each, execution takes 6 seconds total sequentially instead of 2 seconds with asyncio.gather().


History Slicing & Duplicate Persistence Bug

Slicing updated_messages[len(memory.get_context()):] leads to incorrect index offsets because get_context() includes system messages.

Example: The assistant response gets saved to session.json twice—once in the history sync loop and again by memory.add_message("assistant", final_response).

Path Traversal Security Risk

The read_local_file function directly accepts raw file paths without validating directory boundaries.

Example: A prompt leading to read_local_file("../../etc/passwd") allows reading restricted host system files outside the workspace.