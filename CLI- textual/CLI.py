from textual.app import App, ComposeResult
from textual.widgets import Static, Button, Header, Label, Footer, TextLog, Input, DataTable
from textual.widgets import TextLog
from textual.widget import Widget
from textual import events
from textual.containers import Container, Horizontal, Vertical
import time
from textual.reactive import reactive
from rich.text import Text

ROWS = [
    ("lane", "swimmer", "country", "time"),
    (4, "Joseph Schooling", "Singapore", 50.39),
    (2, "Michael Phelps", "United States", 51.14),
    (5, "Chad le Clos", "South Africa", 51.14),
    (6, "László Cseh", "Hungary", 51.14),
    (3, "Li Zhuhao", "China", 51.26),
    (8, "Mehdy Metella", "France", 51.58),
    (7, "Tom Shields", "United States", 51.73),
    (1, "Aleksandr Sadovnikov", "Russia", 51.84),
    (10, "Darren Burns", "Scotland", 51.84),
]


class MainComm(Widget):
    def compose(self) -> ComposeResult:
        yield TextLog(id="text_log_1")
        yield Input(placeholder="messege", id="msg")


class ChatBox(Widget):
    def compose(self) -> ComposeResult:
        logger = TextLog()
        yield logger


class ConnectedUsers(DataTable):
    def on_mount(self) -> None:
        self.add_columns(*ROWS[0])
        for row in ROWS[1:]:
            # Adding styled and justified `Text` objects instead of plain strings.
            styled_row = [
                Text(str(cell), style="italic #03AC13", justify="right") for cell in row
            ]
            self.add_row(*styled_row)

class Connection_box(Widget):
    def compose(self) -> ComposeResult:
        yield ConnectedUsers()
#        yield DataTable(id="athorize")
#        yield DataTable(id="waitnig")



class HorizontalLayout(App):
    CSS_PATH = "horizontal_layout.css"
    TITLE = "SafeChat CLI by Itamar Uliel"
    SUB_TITLE = "***insert time***"

    connected = reactive([])
    msgs = reactive([])
    ready = reactive(False)

    def validate_msgs(self, msgs) -> int:
        self.msgs = msgs
        self.chat_screen.update("\n".join(self.msgs))
        return msgs

    def compose(self) -> ComposeResult:
        yield Header()

        self.mc = MainComm()
        self.chat_box = ChatBox()
        self.conn_box = Connection_box()

        yield self.mc
        yield self.chat_box
        yield self.conn_box

    def on_mount(self):
        self.mc.border_title = "main"
        self.chat_box.border_title = "chat"
        self.conn_box.border_title = "connected"

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.bell()
            app.exit()

    def on_input_submitted(self, input):
        if input.input.id == "pwd":
            self.mc.pwd = input.value

        elif input.input.id == "username":
            self.mc.username = input.value

        if self.mc.username is not None and self.mc.pwd is not None:
            self.login_ready = True
            self.validate_ready(True)

        print(input.value)
        print(input.input)

    def validate_ready(self, is_ready):
        if is_ready:
            app.bell()
        return is_ready


if __name__ == "__main__":
    app = HorizontalLayout()
    app.run()

"""
    BINDINGS = [
        ("r", "add_bar('red')", "Add Red"),
        ("g", "add_bar('green')", "Add Green"),
        ("b", "add_bar('blue')", "Add Blue"),
    ]
    
    def action_add_bar(self, color: str) -> None:
        bar = Bar(color)
        bar.styles.background = Color.parse(color).with_alpha(0.5)
        self.mount(bar)
        self.call_after_refresh(self.screen.scroll_end, animate=False)
"""
