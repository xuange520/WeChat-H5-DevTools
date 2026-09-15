import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

BANNER_TEXT = """
╦ ╦┌─┐╔═╗┬ ┬┌─┐┌┬┐  ╦ ╦╔═╗  ╔╦╗┌─┐┬  ┬╔╦╗┌─┐┌─┐┬  ┌─┐
║║║│  ╠═╣├─┤├─┤ │   ╠═╣╚═╗───║║├┤ └┐┌┘ ║ │ ││ ││  └─┐
╚╩╝└─┘╩ ╩┴ ┴┴ ┴ ┴   ╩ ╩╚═╝  ═╩╝└─┘ └┘  ╩ └─┘└─┘┴─┘└─┘
"""

from .. import __version__

def print_banner():
    banner_panel = Panel(
        f"[bold cyan]{BANNER_TEXT}[/bold cyan]\n"
        "[bold green]微信 4.x 内置浏览器 / 公众号 H5 满血调试与逆向工程套件[/bold green]\n"
        f"[dim]Version {__version__} | High-Performance WeChat H5 Engineering Toolkit[/dim]",
        border_style="bright_blue",
        expand=False
    )
    console.print(banner_panel)

def log_info(msg: str):
    console.print(f"[bold green][+][/bold green] {msg}")

def log_warn(msg: str):
    console.print(f"[bold yellow][!][/bold yellow] {msg}")

def log_error(msg: str):
    console.print(f"[bold red][-][/bold red] {msg}")

def log_step(msg: str):
    console.print(f"[bold cyan][*][/bold cyan] {msg}")

def print_table(title: str, headers: list[str], rows: list[list[str]]):
    table = Table(title=title, border_style="cyan")
    for h in headers:
        table.add_column(h, style="bold white")
    for row in rows:
        table.add_row(*row)
    console.print(table)
