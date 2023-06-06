import socket
import time

import rsa.pkcs1
from rsa.pkcs1 import DecryptionError
from time import sleep

from proj_code.common import *
from proj_code.connection import *


class TUIClientConnectionHandler:

    def __init__(self):
        self.__chat_server = self.__connect_chat_server()
        self.__server_public_key = None
        self.__client_keys = EncryptionUtils.get_keys()
        self.__wconn_socket = None

    @staticmethod
    def __connect_chat_server():
        chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            server_address = ConnectionUtils.get_chat_server_address()
            try:
                chat_server.connect(server_address)
                break
            except TypeError:
                print("currently, there is no chat server to connect to, waiting 10 seconds")
                sleep(10)

            except ConnectionError:
                print("Cannot connect chat server. Waiting 5 seconds")
                sleep(5)
        return chat_server

    def start_listener(self, connection_handler):
        self.__wconn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__wconn_socket.bind((WCONN_IP, 0))
        self.__wconn_socket.listen()
        connection_handler.__send_wconn(WCONN_IP, self.__wconn_socket.getsockname()[1])
        conn, address = self.__wconn_socket.accept()
        return conn

    def do_listen(self, conn):
        try:
            return EncryptionUtils.decrypt(conn.recv(MSG_SIZE), self.__client_keys["pr"])
        except (ConnectionResetError, DecryptionError):
            print("the main server is down. closing connection")
            exit()

    def __send_message(self, msg, to_enc=True):
        if not to_enc:
            try:
                self.__chat_server.send(msg.encode())
            except AttributeError:
                self.__chat_server.send(msg)
        else:
            self.__chat_server.send(EncryptionUtils.encrypt(msg, self.__server_public_key))

    def __receive_message(self, to_decrypt=True):
        if not to_decrypt:
            try:
                data = self.__chat_server.recv(MSG_SIZE)
                return data.decode()
            except Exception:
                return data  # YYY
        else:
            try:
                data = self.__chat_server.recv(MSG_SIZE)
                return EncryptionUtils.decrypt(data, self.__client_keys["pr"])
            except rsa.pkcs1.DecryptionError:
                return data.decode()

    def __send_wconn(self, ip, port):
        try:
            self.__send_message(ChatProtocol.build_set_wconn(ip, port))
            status, msg = ChatProtocol.parse_response(self.__receive_message())
            if status == OK_STATUS:
                pass
        except Exception:
            pass

    def login(self, username, pwd):
            self.__send_message(ChatProtocol.build_login(username, pwd))
            status, msg = ChatProtocol.parse_response(self.__receive_message())
            if status == OK_STATUS:
                print(f"User '{username}' logged in successfully")
                return True
            else:
                print(f"User '{username}' failed to logged in. {msg}")
                return False

    def close_connection(self):
        print(f"closing")
        self.__send_message(ChatProtocol.build_close_connection())
        self.close_all_sockets()

    def start_encrypt(self):
        self.__send_message(ChatProtocol.build_start_encrypt(), False)
        status, msg = ChatProtocol.parse_start_encrypt(self.__receive_message(False))
        if status != OK_STATUS:
            print(f"error while replacing keys. msg: {msg}")
            raise Exception
        self.__send_message(EncryptionUtils.save_public(self.__client_keys["pb"]), False)
        self.__server_public_key = EncryptionUtils.load_public(self.__receive_message(False))

    def authorize(self, username):
        try:
            print(f"authorizing {username}")
            self.__send_message(ChatProtocol.build_authorize(username))
            status, msg = ChatProtocol.parse_response(self.__receive_message())
            if status == OK_STATUS:
                print(msg)
                print(f"User '{username}'asked to authorized")
            else:
                print(f"User '{username}' failed to authorize. {msg}")
        except Exception:
            print("Error during authorize")

    def allow(self, username_to_allow):
        self.__send_message(ChatProtocol.build_allow(username_to_allow))
        status, msg = ChatProtocol.parse_response(self.__receive_message())
        if status == OK_STATUS:
            print(f"User '{username_to_allow}' allowed to send you message")
        else:
            print(f"User '{username_to_allow}' failed to authorize. {msg}")

    def get_connected_users(self):
        try:
            self.__send_message(ChatProtocol.build_get_connected_users())
            connected, authorized = ChatProtocol.parse_response(self.__receive_message())
            return connected, authorized
        except Exception:
            print("Error during get connected users")
            return None, None

    def send_message(self, target_user, msg):
        try:
            self.__send_message(ChatProtocol.build_send_message(target_user, msg))
            status, msg = ChatProtocol.parse_response(self.__receive_message())
            if status == OK_STATUS:
                print(f"message send")
                return True
            else:
                print(f"couldn't send message: {msg}")
                return False
        except Exception:
            print("Error during send_message")
            return False

    def close_all_sockets(self):
        self.__chat_server.close()
        try:
            self.__wconn_socket.close()
        except AttributeError:
            pass

    def see_waiting(self):
        self.__send_message(ChatProtocol.build_see_waiting_client())
        status, msg = ChatProtocol.parse_response(self.__receive_message())
        if status == WAITING_COMMAND:
            return ChatProtocol.parse_see_waiting(msg)
        else:
            print("couldn't get waiting...")
            return None
