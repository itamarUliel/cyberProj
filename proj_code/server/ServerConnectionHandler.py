import socket
import logging
from time import sleep

from proj_code.common import *
from proj_code.connection import *
from proj_code.server import ConnectionData


class ServerConnectionHandler:
    def __init__(self, address):
        self.__address = address
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

    def get_conn_data(self, user):
        return self.__conn_data[user]

    def add_conn_data(self, user):
        self.__conn_data[user] = ConnectionData()

    def remove_conn_data(self, user):
        self.__conn_data.pop(user)

    def get_connected_users(self):
        return self.__connected_users

    def add_connected_user(self, username, user_socket):
        self.__connected_users[username] = user_socket

    def remove_connected_user(self, username):
        self.__connected_users.pop(username)

    def get_connections_list(self):
        return self.__connections_list

    def add_connection(self, connection):
        self.__connections_list.append(connection)

    def remove_connection(self, connection):
        self.__connections_list.remove(connection)
