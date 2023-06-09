from proj_code.common import *
from proj_code.client import *

class ChatClientListener:

    @staticmethod
    def do_listen(connection_handler):
        conn = connection_handler.start_listener(connection_handler)

        while True:
            command, data = ChatProtocol.parse_push_message(connection_handler.do_listen(conn))
            if command == OK_STATUS:
                print(data[0])
            elif command == MSG_COMMAND:
                print(DATA_COLOR + f"got msg from {data[0]}:", PENDING_COLOR + f"{data[1]}")
            elif command == CLOSE_COMMAND:
                connection_handler.close_connection()
                exit("the server close the connection with the wconn")
            else:
                print("the server send an illegal command to wconn, shutting down the client!")
                connection_handler.close_connection()
                break

