"""
from rich import print
from rich.layout import Layout

layout = Layout()

layout.split_column(
    Layout(name="main", size=20, )
)

layout["main"].split_row(
    Layout(name="left"),
    Layout(name="right"),
)
print(layout)
"""
"""
Demonstrates a Rich "application" using the Layout and Live classes.
"""

from datetime import datetime

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel

from rich.table import Table
import keyboard

console = Console()

def make_layout() -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=7),
    )
    layout["main"].split_row(
        Layout(name="left", ratio=2, minimum_size=40),
        Layout(name="right")
        )
    return layout


class Header:
    """Display header with clock."""

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right")
        grid.add_row(
            "[b]safeChat[/b] client CLI",
            datetime.now().ctime().replace(":", "[blink]:[/]"),
        )
        return Panel(grid, style="white on blue")


layout = make_layout()
layout["header"].update(Header())


from rich.live import Live
with Live(layout, refresh_per_second=10, screen=True):
    while True:
        layout["left"].update("hry")
        layout["left"].update("hry\nf")

