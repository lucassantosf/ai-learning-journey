from rich.console import Console

console = Console()

def log_info(message: str):
    console.print(f"[bold blue][INFO][/bold blue] {message}")

def log_error(message: str):
    console.print(f"[bold red][ERROR][/bold red] {message}")

def log_success(message: str):
    console.print(f"[bold green][SUCCESS][/bold green] {message}")