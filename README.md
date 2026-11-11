# Building an LLM Chatbot from Scratch: Evolution & Architecture

A step-by-step engineering journey building an agentic LLM chatbot using **Ollama** and **Python**. This project demonstrates the progression from a simple streaming script to a multi-step, asynchronous agent equipped with memory summarization, tool calling, and real-time telemetry.

---

## Evolution Overview

| Version | Key Focus | Architecture | Memory Strategy | Main Limitation |
| :--- | :--- | :--- | :--- | :--- |
| **v1** | Basic Connection | Monolithic script | Unbounded history | Unstable context, missing error handling |
| **v2** | Architecture & Truncation | Modular classes | Fixed sliding window | Critical information loss across long sessions |
| **v3** | Persistence & Tool Calling | Function registry | File-backed sliding window | Blocking execution, fragile tool handling |
| **v4** | Async & Multi-Step Agent | Non-blocking loop (`asyncio`) | Session-tagged sliding window | Blind message dropping, lack of stream metrics |
| **v5** | Summarization & Telemetry | Fully async + Rich UI | Abstractive memory compression | Event-loop blocking during summary step |

---

## Version Breakdown

### Version 1: The Monolithic Prototype

**Goal:** Establish a basic connection to the local Ollama API and render streamed responses.

#### Features & Improvements
* Integrated basic `ollama.chat()` API with output streaming.
* Real-time text output to the terminal.

#### Limitations & Issues
* **Monolithic Structure:** Entire code resides in a single script without class abstraction.
* **Unbounded Context Window:** Chat history grows indefinitely until hitting local model context limits.
* **Fragile Execution:** No error handling or retry strategy for dropped API connections.
* **Unconfigured Options:** Lacks parameters for temperature, top-p, or system prompt management.

---

### Version 2: Modular Architecture & Memory Truncation

**Goal:** Refactor into modular components and cap context window size.

#### Features & Improvements
* **Decoupled Architecture:** Separated responsibilities into dedicated modules:
  * `client.py`: Ollama API communications.
  * `memory.py`: Sliding-window memory management.
  * `main.py`: Interactive user interface.
* **Sliding Window Memory:** Retained system prompt while trimming older conversation turns (`[-max_history:]`).
* **Configuration Dataclass:** Centralized operational settings (`num_ctx`, `temperature`, `model_name`).
* **Resilient Streaming:** Assistant responses append to history only after clean stream termination.

#### Limitations & Issues
* **Naive Information Loss:** Dropping older messages blindly causes the model to lose key details established earlier in the chat.
* **No External Capabilities:** Purely parametric knowledge; cannot read files or run code.
* **Transient Session State:** Conversation history resets completely whenever the application exits.

---

### Version 3: Function Calling & Local Persistence

**Goal:** Enable local JSON session storage and empower the model to execute local Python functions.

#### Features & Improvements
* **Function/Tool Calling:** Added tool definitions allowing models (e.g., `qwen3.5:4b`) to trigger local functions.
* **JSON Storage:** Saved and loaded conversation history across application restarts.
* **Generation Controls:** Exposed hyperparameters (`temperature`, `num_ctx`, `top_p`) inside client configurations.

#### Limitations & Issues
* **Synchronous / Blocking Execution:** Executing tools freezes the main process. Multi-tool calls run strictly sequentially.
* **Fragile Tool Loop:** 
  * Early `return` statements drop all tool calls after the first one in `message["tool_calls"]`.
  * Context corruption occurs due to duplicate message appends during tool loops.
  * Unhandled tool exceptions crash the application.
* **Raw JSON Storage:** Memory is rewritten to disk entirely on every single message turn without metadata management.
* **Hardcoded Prompts:** No dynamic system prompt adjustment mid-session.

---

### Version 4: Async Engine & Multi-Step Agentic Reasoning

**Goal:** Convert engine to `asyncio` for non-blocking tool calls and build a recursive agent loop.

#### Features & Improvements
* **Asynchronous Engine:** Migrated to `ollama.AsyncClient` for non-blocking requests.
* **Multi-Step Agentic Loop:** Implemented recursive tool calls using a max-turn loop (`max_turns`), allowing the model to chain operations (Tool A $\rightarrow$ Tool B).
* **Multi-Session Management:** Added `session_id` tags and ISO timestamps to local JSON session files.
* **Rich Terminal UI:** Integrated `rich` for structured console feedback during tool calls.

#### Limitations & Issues
* **Blind Sliding Window Loss:** Long conversations still drop critical initial user details (e.g., name, core instructions) once pushed out of `max_history`.
* **Opaque Inference Delay:** Non-streamed `client.chat()` calls create zero-visibility delays while the LLM generates tokens.
* **Uncapped Token Generation:** Missing `num_predict` boundaries leave output generation vulnerable to infinite loops.
* **Default VRAM Unloading:** Unconfigured `keep_alive` values allow Ollama to unload models from GPU VRAM prematurely.

---

### Version 5: Semantic Summarization & Telemetry

**Goal:** Implement long-term abstractive memory compression, real-time UI telemetry, and fine-grained hardware parameters.

#### Features & Improvements
* **In-Memory Semantic Summarization:** Automatically compresses conversation history exceeding a defined threshold into an ongoing executive summary block.
* **Real-Time UI Telemetry:** Live updates on tool executions, arguments, and status changes via `rich.live`.
* **Hardware & VRAM Management:** Added explicit `num_predict` caps and `keep_alive` timers to keep models warmed in GPU memory.
* **Enhanced File Tools:** Added local workspace tools with truncation boundaries.

#### Known Limitations (Identified for v6 Refactoring)
1. **Event Loop Blocking:** Using synchronous `ollama.chat()` inside the `async summarize_if_needed()` call freezes the main thread during context compression.
2. **Naive Summary Appends:** Compounding summaries via simple string concatenation (`self.summary += ...`) causes memory to grow indefinitely over long sessions.
3. **Sequential Async Tool Execution:** Tools inside `run_agent_loop` run sequentially in a `for` loop rather than concurrently with `asyncio.gather()`.
4. **History Slicing & Duplicate Record Bug:** Slicing history with `len(memory.get_context())` leads to index offsets because system prompts are included in context, resulting in duplicate response entries.
5. **Path Traversal Vulnerability:** File-reading tools lack path sanitization, exposing files outside the working directory (e.g., `../../etc/passwd`).
6. **File Reading Truncation & Lack of Pagination:** `read_local_file` hard-truncates at 2,000 characters with no option for pagination offsets.

7. * **Execution Modes:** Supports both interactive Terminal UI (`rich`) for CLI debugging and ASGI web service integration via **Uvicorn / FastAPI**.

### Running Version 5

**Option A: Terminal UI (CLI Mode)**
```bash
python version_5/main.py

---

## Project Setup & Usage

### Prerequisites
* Python 3.10+
* [Ollama](https://ollama.ai/) installed and running locally.

### Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/ollama-chatbot-evolution.git](https://github.com/your-username/ollama-chatbot-evolution.git)
   cd ollama-chatbot-evolution