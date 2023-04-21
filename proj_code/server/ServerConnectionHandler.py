import socket
import logging
from time import sleep

from proj_code.common import *
from proj_code.connection import *


class ServerConnectionHandler:
    def __init__(self, address):
        self.__address = address
        self.__server_keys = None
        self.__server_socket = None

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
