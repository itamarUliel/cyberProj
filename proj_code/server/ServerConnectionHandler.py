import socket

from proj_code.common import *
from proj_code.server import ConnectionData


class ServerConnectionHandler:
    def __init__(self, address):
        self.__address = address
        self.__prime = None          # prime server socket if self is backup server
        self.__prime_address = None  # prime server address if self is backup server
        self.__server_keys = None
        self.__server_socket = None
        self.__conn_data = {}
        self.__connected_users = {}
        self.__connections_list = []

    def start(self):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind(self.__address)
        self.__server_socket.listen()
        print(DATA_COLOR + "START_SERVER: LISTENING AT:", self.__address)

        self.__server_keys = Encryption_handler.get_keys(KEY_SIZE)
        print(OK_COLOR + "START_SERVER: server got keys!", end="\n\n")

    def open_as_backup(self):
        self.__prime, self.__address = self.__server_socket.accept()
        self.__prime.sendall(Encryption_handler.save_public(self.get_server_keys()["pb"]))

    def get_backup_update(self):
        return Encryption_handler.decrypt(self.__prime.recv(RECEIVE_SIZE), self.get_server_keys()["pr"])

    def restart_as_primary(self):
        self.__prime.close()
        self.get_server_socket().close()
        print(ERROR_COLOR + "prime server is down!")
        print(DATA_COLOR + "activate backup!")
        self.start()

    def get_server_socket(self):
        return self.__server_socket

    def get_server_keys(self):
        return self.__server_keys

    def get_private_key(self):
        return self.__server_keys["pr"]

    def get_server_address(self):
        return self.__address

    def get_all_conn_data(self):
        return self.__conn_data

    def get_all_connected_users(self):
        return self.__conn_data.keys()

    def __get_conn_data(self, user):
        return self.__conn_data[user]

    def add_conn_data(self, user):
        self.__conn_data[user] = ConnectionData()

    def close_connection(self, connection):

        username = self.get_username(connection)
        should_update_backup = False

        try:
            self.send_close_message(connection)
        except (AttributeError, ConnectionResetError):
            pass

        try:
            self.__connected_users.pop(username)
        except KeyError:
            pass

        try:
            self.__connections_list.remove(connection)
        except (KeyError, ValueError):
            pass

        try:
            should_update_backup = self.clean_user_authorizations(username)
        except ValueError:
            pass

        try:
            self.__conn_data.pop(connection)
        except KeyError:
            pass
        connection.close()

        return should_update_backup

    def get_connected_users(self):
        return self.__connected_users

    def add_connected_user(self, username, user_socket):
        self.__connected_users[username] = user_socket

    def send_close_message(self, connection):
        self.get_write_socket(connection).sendall(Encryption_handler.encrypt(ChatProtocol.build_close_connection(),
                                                                             self.get_public_key(connection)))
        self.get_write_socket(connection).close()

    def clean_user_authorizations(self, username):
        authorization_found = False
        for user in self.get_all_connected_users():
            try:
                self.get_authorize(user).remove(username)
                authorization_found = True
            except ValueError:
                continue
        return authorization_found

    def get_connections_list(self):
        return self.__connections_list

    def add_connection(self, connection, conn_data=False):
        self.__connections_list.append(connection)
        if conn_data:
            self.__conn_data[connection] = ConnectionData()

    def get_username(self, connection):
        return self.__get_conn_data(connection).get_user()

    def set_username(self, connection, username):
        return self.__get_conn_data(connection).set_user(username)

    def get_authorize(self, connection):
        return self.__get_conn_data(connection).get_authorize()

    def set_authorize(self, connection, to_authorize):
        self.__get_conn_data(connection).set_authorize(to_authorize)

    def update_authorize(self, connection, to_authorize):
        self.__get_conn_data(connection).update_authorize(to_authorize)

    def get_status(self, connection):
        return self.__get_conn_data(connection).get_status()

    def set_status(self, connection, status):
        self.__get_conn_data(connection).set_status(status)

    def get_public_key(self, connection):
        return self.__get_conn_data(connection).get_public_key()

    def set_public_key(self, connection, public_key):
        self.__get_conn_data(connection).set_public_key(public_key)

    def get_write_socket(self, connection):
        return self.__get_conn_data(connection).get_write_socket()

    def set_write_socket(self, connection, write_socket):
        return self.__get_conn_data(connection).set_write_socket(write_socket)
