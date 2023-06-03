from textual.app import App, ComposeResult
from textual.widgets import Static, Header, TextLog, Label, Footer, TextLog, Input, LoadingIndicator, DataTable, RadioSet
from textual.widget import Widget
from textual import events
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from screens import LOGIN_SCREEN, second_screen
from TUIChatClient import *
import sys, time
original_stdout = sys.stdout
import threading
from os import dup
from proj_code.common.colors import LOGO

class LoginScreen(Screen):
    def __init__(self, chat_client):
        super().__init__()
        self.login_screen = LOGIN_SCREEN()
        self.textLogger: TextLog
        self.__username = None
        self.__pwd = None

        self.chat_client: TUIChatClient = chat_client

    BINDINGS = []

    def compose(self) -> ComposeResult:
        yield self.login_screen
        yield Header(show_clock=True)
        yield Footer()

    def _on_mount(self, event: events.Mount) -> None:
        self.textLogger = self.login_screen.get_logger()
        sys.stdout = self.textLogger
        print(LOGO)
        self.chat_client.activate()
        self.chat_client.start_encrypt()

    def on_input_changed(self, input):
        if input.input.id == "passwordLogin":
            self.__pwd = input.value

        if input.input.id == "usernameLogin":
            self.__username = input.value

    def on_input_submitted(self, input):
        if input.input.id == "passwordLogin":
            self.__pwd = input.value
            input.input.value = ""

        if input.input.id == "usernameLogin":
            self.__username = input.value

        if self.__username is not None and self.__pwd is not None:
            self.send_login()

    def send_login(self):
        if self.chat_client.login(self.__username, self.__pwd):
            app.push_screen('MainScreen')


class MainScreen(Screen):
    BINDINGS = [("r", "refresh_users()", "refresh")]
    def __init__(self, chat_client):
        super().__init__()
        self.authorize_user = None
        self.waiting_user = None
        self.connected_user = None

        self.main_screen = second_screen()
        self.dataLog: TextLog
        self.wconnLog: TextLog

        self.chat_client: TUIChatClient = chat_client
        self.descriptor = dup(0)

    def reopen_stdin(self):
        sys.stdin = open(self.__stdin_descriptor)
        self.__stdin_descriptor = dup(0)

    def compose(self) -> ComposeResult:
        yield self.main_screen
        yield Header(show_clock=True)
        yield Footer()

    def _on_mount(self, event: events.Mount) -> None:
        self.dataLog = self.main_screen.get_data_logger()
        self.wconnLog = self.main_screen.get_wconn_logger()
        sys.stdout = self.dataLog
        self.chat_client.set_wconn_logger(self.wconnLog)
        self.chat_client.start_listener()
        time.sleep(1)
        self.refresh_user()

    def refresh_user(self):
        connected, authorize = self.chat_client.get_connected_users()
        waiting = self.chat_client.see_waiting()
        self.load_waiting(waiting)
        self.load_connected(connected)
        self.load_authorize(authorize)
        self.dataLog.write("user refreshed!")

    def action_refresh_users(self):
        self.refresh_user()

    def on_input_submitted(self, input):
        if input.input.id == "msgInput":
            self.message = input.value
            input.input.value = ""
        self.dataLog.write(self.authorize_user)
        if self.authorize_user is None or self.authorize_user == "":
            self.dataLog.write("please select user!")
        else:
            sent = self.chat_client.send_message(self.authorize_user, self.message)
            if sent:
                self.wconnLog.write(f"from Me to '{self.authorize_user}': {self.message}")

    def on_radio_set_changed(self, radio_set):
        try:
            radio_set_id = radio_set.radio_set.id
            if radio_set_id == "waiting":
                self.waiting_user = self.get_waiting_username()
                self.chat_client.allow(self.waiting_user)
                self.refresh_user()

            elif radio_set_id == "connected":
                self.connected_user = self.get_connected_username()
                self.chat_client.authorize(self.connected_user)
                self.refresh_user()

            elif radio_set_id == "authorize":
                self.authorize_user = self.get_authorize_username()
                self.refresh_user()
        except ValueError:
            self.reopen_stdin()

    def load_authorize(self, lst):
        return self.main_screen.second.authorized.load_buttons(RadioSet(*lst, id="authorize"))

    def get_authorize_username(self):
        return self.main_screen.second.authorized.get_username()

    def load_waiting(self, lst):
        return self.main_screen.second.waiting.load_buttons(RadioSet(*lst, id="waiting"))

    def get_waiting_username(self):
        return self.main_screen.second.waiting.get_username()

    def load_connected(self, lst):
        return self.main_screen.second.connected.load_buttons(RadioSet(*lst, id="connected"))

    def get_connected_username(self):
        return self.main_screen.second.connected.get_username()


class ChatApp(App):
    global full_time
    TITLE = "SafeChat CLI by Itamar Uliel"
    CSS_PATH = "login_screen.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    chat_client = TUIChatClient()
    SCREENS = {"MainScreen": MainScreen(chat_client), "LoginScreen": LoginScreen(chat_client)}

    def __init__(self):
        super().__init__()

    def on_mount(self):
        try:
            self.push_screen("LoginScreen")
        except ConnectionError:
            self.chat_client.restart_conn_handler()


if __name__ == "__main__":
    app = ChatApp()
    app.run()