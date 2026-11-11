import asyncio
from rich.console import Console
from rich.panel import Panel
from config import Config
from memory import SummarizedMemory
from client import TelemetryOllamaAgent

console = Console()

async def main():
    cfg = Config()
    memory = SummarizedMemory(
        storage_dir=cfg.storage_dir,
        session_id=cfg.session_id,
        system_prompt=cfg.system_prompt,
        max_history=cfg.max_history_messages,
        threshold=cfg.summary_threshold,
        model_name=cfg.model_name
    )
    agent = TelemetryOllamaAgent(
        model_name=cfg.model_name,
        temperature=cfg.temperature,
        num_ctx=cfg.num_ctx,
        num_predict=cfg.num_predict,
        keep_alive=cfg.keep_alive
    )

    console.print(Panel(
        f"[bold green]Ollama Chatbot v5 Engine[/bold green]\n"
        f"Model: [cyan]{cfg.model_name}[/cyan] | Session: [yellow]{cfg.session_id}[/yellow]\n"
        f"Memory Compression: [magenta]Active (Threshold={cfg.summary_threshold})[/magenta]"
    ))

    async def log_telemetry(msg: str):
        console.print(f"  └─ {msg}")

    while True:
        try:
            user_input = console.input("[bold blue]You:[/bold blue] ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit"]:
            break

        if user_input.lower() == "clear":
            memory.clear()
            console.print("[bold red]Session memory wiped.[/bold red]\n")
            continue

        memory.add_message("user", user_input)
        
        # Background memory summarization check
        await memory.summarize_if_needed()

        try:
            console.print("[dim]Processing context and tool states...[/dim]")
            final_response, updated_messages = await agent.run_agent_loop(
                messages=memory.get_context(),
                telemetry_callback=log_telemetry
            )
            
            # Sync newly executed messages back to history store
            for new_msg in updated_messages[len(memory.get_context()):]:
                memory.add_message(
                    role=new_msg["role"],
                    content=new_msg.get("content", ""),
                    name=new_msg.get("name")
                )

            console.print(f"[bold green]Assistant:[/bold green] {final_response}\n")
            memory.add_message("assistant", final_response)

        except Exception as e:
            console.print(f"[bold red]Execution Error:[/bold red] {e}\n")

if __name__ == "__main__":
    asyncio.run(main())