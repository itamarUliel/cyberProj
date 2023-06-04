from textual.app import App, ComposeResult
from textual.widgets import Static, Header, TextLog, Label, Footer, TextLog, Input, LoadingIndicator, DataTable, \
    RadioSet, RadioButton
from textual.widget import Widget
from textual import events
from textual.containers import Container, Horizontal, Vertical
import time
from textual.reactive import reactive
from textual.screen import Screen
import threading
from proj_code.common.colors import SMALL_FULL_LOGO, FULL_LOGO, LOGO


class Upper(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.__logger = Logger()
        self.__wconn = Wconn()

    def compose(self) -> ComposeResult:
        yield self.__logger
        yield self.__wconn

    def _on_mount(self, event: events.Mount) -> None:
        self.__wconn.border_title = "chat box - received message"

    def get_data_logger(self):
        return self.__logger.get_data_loger()

    def get_wconn_logger(self):
        return self.__wconn.get_wconn_logger()

    def get_msg_input(self):
        return self.__logger.get_msg_input()


class Wconn(Widget):
    def compose(self) -> ComposeResult:
        self.__wconn_logger = TextLog(id="wconnLogger")
        yield self.__wconn_logger

    def get_wconn_logger(self):
        return self.__wconn_logger


class Logger(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.__data_logger = TextLog(id="dataLoger")
        self.__msg_input = Input(id="msgInput", placeholder="write message here")

    def compose(self) -> ComposeResult:
        yield self.__data_logger
        yield self.__msg_input

    def _on_mount(self, event: events.Mount) -> None:
        self.__data_logger.border_title = "server communication box"


    def get_data_loger(self):
        return self.__data_logger

    def get_msg_input(self):
        return self.__msg_input


class Second(Widget):
    def compose(self) -> ComposeResult:
        self.connected = Connected()
        self.authorized = Authorized()
        self.waiting = Waiting()

        yield self.connected
        yield self.authorized
        yield self.waiting

    def on_mount(self):
        self.connected.border_title = "Connected - send friend request"
        self.authorized.border_title = "Authorized - send message"
        self.waiting.border_title = "Waiting - allow friend request"


class Authorized(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.radio_set: RadioSet = None
        self.container = Container(id="AuthorizeSets")

    def compose(self, update=None) -> ComposeResult:
        yield self.container

    def load_buttons(self, radio_bottom):
        if self.radio_set is not None:
            self.radio_set.remove()
        self.query_one("#AuthorizeSets").mount(radio_bottom)
        self.radio_set = radio_bottom

    def get_username(self):
        if self.radio_set is None:
            return None
        if self.radio_set.pressed_button is None:
            return None
        return self.radio_set.pressed_button.label


class Waiting(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.radio_set: RadioSet = None
        self.container = Container(id="WaitingSets")

    def compose(self, update=None) -> ComposeResult:
        yield self.container

    def load_buttons(self, radio_bottom):
        if self.radio_set is not None:
            self.radio_set.remove()
        self.query_one("#WaitingSets").mount(radio_bottom)
        self.radio_set = radio_bottom

    def get_username(self):
        if self.radio_set is None:
            return None
        if self.radio_set.pressed_button is None:
            return None
        return self.radio_set.pressed_button.label


class Connected(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.radio_set: RadioSet = None
        self.container = Container(id="ConnectedSets")

    def compose(self, update=None) -> ComposeResult:
        yield self.container

    def load_buttons(self, radio_bottom):
        if self.radio_set is not None:
            self.radio_set.remove()
        self.query_one("#ConnectedSets").mount(radio_bottom)
        self.radio_set = radio_bottom

    def get_username(self):
        if self.radio_set is None:
            return None
        if self.radio_set.pressed_button is None:
            return None
        return self.radio_set.pressed_button.label


class second_screen(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.__upper = Upper()
        self.second = Second()

    def compose(self) -> ComposeResult:
        yield self.__upper
        yield self.second

    def get_data_logger(self):
        return self.__upper.get_data_logger()

    def get_wconn_logger(self) -> TextLog:
        return self.__upper.get_wconn_logger()

    def get_msg_input(self):
        return self.__upper.get_msg_input()


class LOGIN_SCREEN(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.text_logger = TextLog(id="loginTextLog")
        self.userInput = Input(placeholder="username", id="usernameLogin")
        self.pwdInput = Input(placeholder="password", password=True, id="passwordLogin")
        self.load = LoadingIndicator(id="loading")

    def compose(self) -> ComposeResult:
        yield self.userInput
        yield self.pwdInput
        yield self.load
        yield self.text_logger

    def get_logger(self):
        return self.text_logger

    """
    def _on_mount(self, event: events.Mount) -> None:
        self.text_logger.styles.animate("opacity", value=0.0, duration=8.0, delay=2.0)
        self.userInput.styles.animate("opacity", value=0.0, duration=8.0, delay=2.0)
        self.pwdInput.styles.animate("opacity", value=0.0, duration=8.0, delay=2.0)
        self.load.styles.animate("opacity", value=0.0, duration=8.0, delay=2.0)
    """


class ConncetedScreen(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.label = Label("click to connect connection server".rjust(30), id="textLabel")
        self.logo = Label(LOGO, id="logoLabel")
        self.load = LoadingIndicator(id="loadingLogin")
        self.container = Vertical(id="login_container")

    def compose(self) -> ComposeResult:
        yield self.logo
        yield self.load
        yield self.container

    def _on_mount(self, event: events.Mount) -> None:
        self.logo.styles.animate("opacity", value=100.0, duration=7.0)
        self.load.styles.animate("opacity", value=100.0, duration=7.0)
        self.query_one("#login_container").mount(self.label)
        self.label.styles.animate("opacity", value=100.0, duration=7.0)

    def replace_text(self, text: str, delay: int = 0):
        self.label.remove()
        self.label = Label(text, id="textLabel")
        self.query_one("#login_container").mount(self.label)
        self.label.styles.animate("opacity", value=100.0, duration=10, delay=delay)

    @staticmethod
    def blink_label(label):
        label.styles.animate("opacity", value=0.0, duration=3.0, delay=2.0)
        label.styles.animate("opacity", value=100.0, duration=6.0, delay=5.0)

