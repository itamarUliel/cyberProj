from chat_server import *
from network_utils import *
from server_handler import *
from colors import *


def main():
    prime = ChatServer(True, PRIMARY_ADDRESS)
    prime.start_running()


if __name__ == '__main__':
    main()