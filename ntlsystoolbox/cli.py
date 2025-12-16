from rich.console import Console
from rich.panel import Panel

console = Console()

def show_logo():
    console.print(Panel("NTL-SysToolbox", style="bold cyan"))

def main_menu():
    console.print("[1] Diagnostic")
    console.print("[2] WMS Backup")
    console.print("[3] Obsolescence Audit")
    console.print("[T] UI Settings")
    console.print("[Q] Quit")

def main():
    show_logo()
    while True:
        main_menu()
        choice = input("> ").lower()

        if choice == "q":
            console.print("Bye.", style="dim")
            break
