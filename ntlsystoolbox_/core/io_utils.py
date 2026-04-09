from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import questionary

console = Console()

def print_header(title: str, subtitle: str = ""):
    console.print(Panel(Text(subtitle, justify="center"), title=title, expand=False, style="bold cyan"))

def print_success(message: str):
    console.print(f"[bold green]✔ {message}[/bold green]")

def print_error(message: str):
    console.print(f"[bold red]✘ {message}[/bold red]")

def print_warning(message: str):
    console.print(f"[bold yellow]! {message}[/bold yellow]")

def print_info(message: str):
    console.print(f"[blue]i[/blue] {message}")

def confirm_action(message: str) -> bool:
    return questionary.confirm(message).ask()

def select_option(message: str, choices: list) -> str:
    return questionary.select(message, choices=choices).ask()

def wait_for_enter(message: str = "Press Enter to continue..."):
    questionary.press_any_key_to_continue(message).ask()
