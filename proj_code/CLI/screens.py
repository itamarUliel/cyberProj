from textual.app import App, ComposeResult
from textual.widgets import Static, Header, TextLog, Label, Footer, TextLog, Input, LoadingIndicator, DataTable, RadioSet, RadioButton
from textual.widget import Widget
from textual import events
from textual.containers import Container, Horizontal, Vertical
import time
from textual.reactive import reactive
from textual.screen import Screen
import threading
class Upper(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.__logger = Logger()
        self.__wconn = Wconn()

    def compose(self) -> ComposeResult:
        yield self.__logger
        yield self.__wconn

    def get_data_logger(self):
        return self.__logger.get_data_loger()

    def get_wconn_logger(self):
        return self.__wconn.get_wconn_logger()


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

    def get_data_loger(self):
        return self.__data_logger


class Second(Widget):
    def compose(self) -> ComposeResult:
        self.connected = Connected()
        self.authorized = Authorized()
        self.waiting = Waiting()

        yield self.connected
        yield self.authorized
        yield self.waiting

    def on_mount(self):
        self.connected.border_title = "Connected"
        self.authorized.border_title = "Authorized"
        self.waiting.border_title = "Waiting"


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


class LOGIN_SCREEN(Widget):
    def __init__(self, *children: Widget):
        super().__init__(*children)
        self.text_logger = TextLog(id="loginTextLog")
        self.userInput = Input(placeholder="username", id="usernameLogin")
        self.pwdInput = Input(placeholder="password", password=True, id="passwordLogin")

    def compose(self) -> ComposeResult:
        yield self.userInput
        yield self.pwdInput
        yield LoadingIndicator(id="loading")
        yield self.text_logger

    def get_logger(self):
        return self.text_logger
