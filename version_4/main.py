import asyncio
from rich.console import Console
from rich.panel import Panel
from config import Config
from memory import StructuredMemory
from client import AsyncOllamaAgent

console = Console()

async def main():
    cfg = Config()
    memory = StructuredMemory(
        storage_dir=cfg.storage_dir,
        session_id=cfg.session_id,
        system_prompt=cfg.system_prompt,
        max_history=cfg.max_history_messages
    )
    agent = AsyncOllamaAgent(
        model_name=cfg.model_name,
        temperature=cfg.temperature,
        num_ctx=cfg.num_ctx
    )

    console.print(Panel(f"[bold green]Ollama Chatbot v4[/bold green]\nModel: [cyan]{cfg.model_name}[/cyan] | Session: [yellow]{cfg.session_id}[/yellow]"))

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
            console.print("[bold red]Session memory cleared.[/bold red]\n")
            continue

        memory.add_message("user", user_input)

        with console.status("[bold yellow]Thinking & executing tools...[/bold yellow]"):
            try:
                final_response, updated_messages = await agent.run_agent_loop(memory.get_context())
                
                # Sync new messages (including tool steps) back into persistent memory
                for new_msg in updated_messages[len(memory.get_context()):]:
                    memory.add_message(
                        role=new_msg["role"],
                        content=new_msg.get("content", ""),
                        name=new_msg.get("name")
                    )

                console.print(f"[bold green]Assistant:[/bold green] {final_response}\n")
                memory.add_message("assistant", final_response)

            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {e}\n")

if __name__ == "__main__":
    asyncio.run(main())