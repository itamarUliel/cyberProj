from os import dup
import sys
from threading import Thread
import time
from TUIChatClientListener import *
from TUIClientConnectionHandler import *


class TUIChatClient:
    def __init__(self):
        self.__user_backup = None
        self.__conn_handler: TUIClientConnectionHandler
        self.__listener = None
        self.__stdin_descriptor = dup(0)
        self.__wconn_logger = None

    def set_wconn_logger(self, logger):
        self.__wconn_logger = logger

    def activate(self):
        self.__conn_handler = TUIClientConnectionHandler()

    def start_listener(self):
        self.__listener = Thread(target=TUIChatClientListener.do_listen, args=[self.__conn_handler, self.__wconn_logger], daemon=True).start()

    def close_connection(self):
        self.__conn_handler.close_connection()
        exit()

    def reopen_stdin(self):
        sys.stdin = open(self.__stdin_descriptor)
        self.__stdin_descriptor = dup(0)

    def authorize(self, username):
        self.__conn_handler.authorize(username)

    def allow(self, username):
        self.__conn_handler.allow(username)

    def send_message(self, username, msg):
        chk = self.__conn_handler.send_message(username, msg)
        return chk

    def see_waiting(self):
        return self.__conn_handler.see_waiting()

    def get_connected_users(self):
        try:
            conn, auth = self.__conn_handler.get_connected_users()
            return conn.split(","), auth.split(",")
        except AttributeError:
            raise ConnectionError

    def login(self, user, password):
        valid_user = False
        try:

            if self.__user_backup is None:
                username, pwd = user, password
            else:
                username, pwd = self.__user_backup

            valid_user = self.__conn_handler.login(username, pwd)
            if valid_user:
                self.__user_backup = (username, pwd)
                return True
            else:
                self.__user_backup = None
                return False
        except IndexError:
            valid_user = False
            return False

    def start_encrypt(self):
        self.__conn_handler.start_encrypt()

    def restart_conn_handler(self):
        self.__conn_handler.close_all_sockets()
        self.__conn_handler = TUIClientConnectionHandler()

    def run(self):
        self.start_encrypt()
        self.login()
        self.start_listener()

        while True:
            show = """\n
                        'f' = send a 'friend request' to some to send them message
                        'm' = write a message
                        'e' = close connection (exit)
                        'c' = see who's connected and who you can talk to
                        'w' = see who's waiting to get authorize by you
                        'a' = allow someone to send you message
                        """
            print(show)
            try:
                act = input("\t\t\tact:")[0]
            except IndexError:
                print("try again...")
                continue

            except ValueError:
                self.reopen_stdin()
                act = input("\t\t\tact:")[0]

            if act in ['f', 'm', 'e', 'c', 'w', 'a']:
                if act == 'e':
                    self.close_connection()
                elif act == 'f':
                    self.authorize()
                elif act == 'c':
                    self.get_connected_users()
                elif act == 'm':
                    self.send_message()
                elif act == 'w':
                    self.see_waiting()
                elif act == 'a':
                    self.allow()


def start_client():
    chat_client = ChatClient()
    while True:
        try:
            chat_client.run()
        except ConnectionError:
            chat_client.restart_conn_handler()
            continue
