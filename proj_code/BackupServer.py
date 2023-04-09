from chat_server import BackupServer, ChatServer
from network_utils import *
from server_handler import *
from colors import *


def main():
    backup = ChatServer(False, SECONDARY_ADDRESS)
    backup.start_running()


if __name__ == '__main__':
    main()


