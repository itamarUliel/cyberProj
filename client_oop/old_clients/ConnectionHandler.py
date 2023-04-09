import http.client
import socket
import logging
from connection_utils import *
from time import sleep
from ChatProtocol import *
import Encryption_handler


class ConnectionHandler:

    @classmethod
    def get_server_address(cls, server_type):
        try:
            connection = http.client.HTTPConnection(f"{CONNECTION_SERVER_IP}:{CONNECTION_SERVER_PORT}")
            connection.request("GET", f"/{server_type}")
            address = connection.getresponse().read().decode().split(":")
            return (address[0], int(address[1]))
        except ConnectionError:
            logging.error("Error Connecting Connection Server")
            return None
        except ValueError:
            logging.error(f"Invalid address received for {server_type}")
            return None

    def __connect_server(self, server_type):
        self.__servers_sockets.get(server_type).connect(self.__servers_addresses.get(server_type))
        logging.info(f"{server_type} connected")

    def __init__(self):
        self.__client_keys = Encryption_handler.get_keys()
        self.__server_public_key = None

        self.__servers_addresses = {PRIMARY_NAME: ConnectionHandler.get_server_address(PRIMARY_NAME),
                                    SECONDARY_NAME: ConnectionHandler.get_server_address(SECONDARY_NAME)}

        self.__servers_sockets = {PRIMARY_NAME: socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                                  SECONDARY_NAME: socket.socket(socket.AF_INET, socket.SOCK_STREAM)}

        self.__connected_server = None
        while self.__connected_server is None:
            try:
                self.__connect_server(PRIMARY_NAME)
                self.__connected_server = self.__servers_sockets.get(PRIMARY_NAME)
            except ConnectionError:
                try:
                    self.__connect_server(SECONDARY_NAME)
                    self.__connected_server = self.__servers_sockets.get(SECONDARY_NAME)
                except ConnectionError:
                    logging.error("Cannot connect chat server. Waiting few seconds")
                    sleep(3)

        self.__start_wconn()   ###

    def __get_server(self):
        return self.__connected_server

    def __switch_server(self):
        if self.__connected_server == self.__servers_sockets.get(PRIMARY_NAME):
            self.__connect_server(SECONDARY_NAME)
            self.__connected_server = self.__servers_sockets.get(SECONDARY_NAME)
            logging.info("Server switched")
        else:
            logging.error("Error switching server")

    def __send_message(self, msg, to_enc=True):
        if not to_enc:
            self.__get_server().send(msg.encode())
        else:
            self.__get_server().send(Encryption_handler.encrypt(msg, self.__server_public_key))

    def __receive_message(self, to_decrypt=True):
        if not to_decrypt:
            return self.__get_server().recv(MSG_SIZE)
        else:
            return Encryption_handler.decrypt(self.__get_server().recv(MSG_SIZE), self.__client_keys["pr"])

    def login(self, username, pwd):
        try:
            self.__send_message(ChatProtocol.build_login(username, pwd))
            status, msg = ChatProtocol.parse_login(self.__receive_message())
            if status == OK_STATUS:
                logging.info(f"User '{username}' logged in successfully")
                return True
            else:
                logging.warning(f"User '{username}' failed to logged in. {msg}")
                return False
        except Exception:
            logging.error("Error during login")
            return False

    def close_connection(self):
        logging.info(f"closing")
        self.__send_message(ChatProtocol.build_close_connection())

    def authorize(self, username):
        try:
            logging.info(f"authorizing {username}")
            self.__send_message(ChatProtocol.build_authorize(username))
            status, msg = ChatProtocol.parse_authorize(self.__receive_message())
            if status == OK_STATUS:
                logging.info(f"User '{username}' authorized")
            else:
                logging.warning(f"User '{username}' failed to authorize. {msg}")
        except Exception:
            logging.error("Error during authorize")

    def get_connected_users(self):
        try:
            self.__send_message(ChatProtocol.build_get_connected_users())
            connected, authorized = ChatProtocol.parse_connected(self.__receive_message())
            return connected, authorized
        except Exception:
            logging.error("Error during get connected users")
            return None, None

    def send_message(self, target_user, msg):
        try:
            self.__send_message(ChatProtocol.build_send_message(target_user, msg))
            status, msg = ChatProtocol.parse_send_message(self.__receive_message())
            if status == OK_STATUS:
                logging.info(f"message send")
            else:
                logging.warning(f"couldn't send message: {msg}")
        except Exception:
            logging.error("Error during send_message")

    def start_encrypt(self):
        self.__send_message(ChatProtocol.build_start_encrypt(), False)
        status, msg = ChatProtocol.parse_start_encrypt(self.__receive_message(False))
        if status != OK_STATUS:
            logging.error(f"error while replacing keys. msg: {msg}")
            raise Exception
        self.__send_message(Encryption_handler.save_public(self.__keys["pb"]), False)
        self.__server_public_key = Encryption_handler.load_public(self.__receive_message(False))


def main():
    logging.basicConfig(level=logging.INFO)
#    assert ConnectionHandler.get_server_address(PRIMARY_NAME) == (PRIMARY_IP, PRIMARY_PORT)
#    assert ConnectionHandler.get_server_address(SECONDARY_NAME) == (SECONDARY_IP, SECONDARY_PORT)
    ch = ConnectionHandler()
    ch.login("user1", "pwd1")


if __name__ == '__main__':
    main()