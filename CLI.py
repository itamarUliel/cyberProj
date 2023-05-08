from textual.app import App, ComposeResult
from textual.widgets import Static, Button, Header, Label, Footer, TextLog, Input
from textual.widget import Widget
from textual import events
from textual.containers import Container, Horizontal, Vertical
import time
from textual.reactive import reactive
from proj_code.client import *



class MainComm(Widget):
    def compose(self) -> ComposeResult:
        self.username = Input(placeholder="Username",id="username")
        self.pwd = Input(placeholder="pwd", password=True, id="pwd")
        yield self.username
        yield self.pwd

class ChatBox(Widget):
    pass

class Connection_box(Widget):
    pass


class HorizontalLayoutExample(App):
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
            self.pwd = input.value

        elif input.input.id == "username":
            self.username = input.value

        if self.username is not None and self.pwd is not None:
            self.login_ready = True

        print(input.value)
        print(input.input)

    def validate_ready(self, is_ready):
        if is_ready:
            app.bell()
        return is_ready





if __name__ == "__main__":
    app = HorizontalLayoutExample()
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