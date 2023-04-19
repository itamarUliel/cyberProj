from proj_code.common import *
from proj_code.server import *

def main():
    backup = ChatServer(False, SECONDARY_ADDRESS)
    backup.start_running()


if __name__ == '__main__':
    main()


