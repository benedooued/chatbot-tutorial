# This version 1 


Lacks of Unbounded Context Window, 
Has a monolithic structure,
No configuration management and a very poor error handling. 
It is a simple chatbot that interacts with the Ollama API in a streaming manner.


For the version 2, we are going to:

Decoupled Architecture: Separate the client (Ollama communication), memory management (context trimming), and user interface into modular classes/modules.

Sliding Window Memory: Retain the original system prompt while dynamically truncating older conversation turns to cap memory size

Configuration Object: Centralize variables in a configurable dictionary or dataclass.

Resilient Streaming State: Only append the assistant's message to history if the stream finishes cleanly without exceptions.