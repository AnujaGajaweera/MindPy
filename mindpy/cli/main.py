"""
Main CLI entry point for MindPy.

Provides command-line interface for controlling bots.
"""

import asyncio
import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from mindpy.bot import Bot
from mindpy.bot.manager import BotManager
from mindpy.config import Config
from mindpy.logging import setup_logging, get_logger

app = typer.Typer(help="MindPy - Python AI framework for Minecraft bots")
console = Console()
logger = get_logger(__name__)


@app.command()
def run(
    host: str = typer.Option("localhost", help="Server host"),
    port: int = typer.Option(25565, help="Server port"),
    username: str = typer.Option("MindPyBot", help="Bot username"),
    config: Optional[str] = typer.Option(None, help="Config file path"),
    log_level: str = typer.Option("INFO", help="Log level")
):
    """
    Run a MindPy bot.
    """
    # Setup logging
    setup_logging(level=log_level)
    
    # Load config if provided
    cfg = Config(config) if config else Config()
    
    # Create and run bot
    async def _run():
        bot = Bot(
            host=host,
            port=port,
            username=username,
            config=cfg
        )
        
        console.print(f"[bold green]Starting MindPy bot[/bold green]")
        console.print(f"Host: {host}:{port}")
        console.print(f"Username: {username}")
        
        try:
            await bot.connect()
            await bot.run()
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down...[/yellow]")
        finally:
            await bot.disconnect()
    
    asyncio.run(_run())


@app.command()
def connect(
    host: str = typer.Argument(..., help="Server host"),
    port: int = typer.Argument(25565, help="Server port"),
    username: str = typer.Argument(..., help="Bot username")
):
    """
    Connect to a Minecraft server.
    """
    async def _connect():
        bot = Bot(host=host, port=port, username=username)
        
        console.print(f"Connecting to {host}:{port} as {username}...")
        
        try:
            await bot.connect()
            console.print("[bold green]Connected successfully![/bold green]")
            await bot.disconnect()
        except Exception as e:
            console.print(f"[bold red]Connection failed: {e}[/bold red]")
    
    asyncio.run(_connect())


@app.command()
def plugins(
    list_plugins: bool = typer.Option(False, "--list", "-l", help="List plugins"),
    enable: Optional[str] = typer.Option(None, "--enable", "-e", help="Enable plugin"),
    disable: Optional[str] = typer.Option(None, "--disable", "-d", help="Disable plugin")
):
    """
    Manage plugins.
    """
    if list_plugins:
        console.print("[bold]Available plugins:[/bold]")
        # TODO: List actual plugins
        console.print("No plugins loaded")
    
    if enable:
        console.print(f"Enabling plugin: {enable}")
        # TODO: Enable plugin
    
    if disable:
        console.print(f"Disabling plugin: {disable}")
        # TODO: Disable plugin


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show config"),
    set_config: Optional[str] = typer.Option(None, "--set", help="Set config key=value"),
    config_file: Optional[str] = typer.Option(None, help="Config file path")
):
    """
    Manage configuration.
    """
    cfg = Config(config_file) if config_file else Config()
    
    if show:
        console.print("[bold]Current configuration:[/bold]")
        table = Table()
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in cfg.to_dict().items():
            table.add_row(key, str(value))
        
        console.print(table)
    
    if set_config:
        if "=" not in set_config:
            console.print("[bold red]Invalid format. Use key=value[/bold red]")
            return
        
        key, value = set_config.split("=", 1)
        cfg.set(key, value)
        cfg.save()
        console.print(f"Set {key} = {value}")


@app.command()
def chat(
    host: str = typer.Option("localhost", help="Server host"),
    port: int = typer.Option(25565, help="Server port"),
    username: str = typer.Option("MindPyBot", help="Bot username")
):
    """
    Run a chat-enabled bot.
    """
    async def _chat():
        bot = Bot(host=host, port=port, username=username)
        
        console.print(f"[bold green]Starting chat bot[/bold green]")
        
        try:
            await bot.connect()
            console.print("Type messages to send to chat (Ctrl+C to exit)")
            
            while True:
                message = console.input("[bold cyan]Chat:[/bold cyan] ")
                if message:
                    await bot.chat(message)
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down...[/yellow]")
        finally:
            await bot.disconnect()
    
    asyncio.run(_chat())


@app.command()
def shell(
    host: str = typer.Option("localhost", help="Server host"),
    port: int = typer.Option(25565, help="Server port"),
    username: str = typer.Option("MindPyBot", help="Bot username")
):
    """
    Run an interactive shell for controlling the bot.
    """
    async def _shell():
        bot = Bot(host=host, port=port, username=username)
        
        console.print(f"[bold green]Starting MindPy shell[/bold green]")
        console.print("Type 'help' for available commands")
        
        try:
            await bot.connect()
            
            while True:
                command = console.input("[bold cyan]mindpy>[/bold cyan] ")
                
                if command == "help":
                    console.print("Available commands:")
                    console.print("  help    - Show this help")
                    console.print("  status  - Show bot status")
                    console.print("  exit    - Exit shell")
                elif command == "status":
                    console.print(f"Connected: {bot.is_connected()}")
                    console.print(f"Position: {bot.get_position()}")
                    console.print(f"Health: {bot.get_health()}")
                    console.print(f"Hunger: {bot.get_hunger()}")
                elif command == "exit":
                    break
                else:
                    console.print(f"Unknown command: {command}")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down...[/yellow]")
        finally:
            await bot.disconnect()
    
    asyncio.run(_shell())


@app.command()
def benchmark(
    duration: int = typer.Option(60, help="Benchmark duration in seconds")
):
    """
    Run performance benchmarks.
    """
    console.print(f"[bold green]Running benchmarks for {duration}s[/bold green]")
    # TODO: Implement actual benchmarks
    console.print("Benchmarks not yet implemented")


@app.command()
def version():
    """Show MindPy version."""
    from mindpy import __version__
    console.print(f"MindPy version: {__version__}")


def cli():
    """Main CLI entry point."""
    app()


if __name__ == "__main__":
    cli()
