from proj_code.common import *
from proj_code.client import *
class TUIChatClientListener:

    @staticmethod
    def do_listen(connection_handler, text_logger):
        conn = connection_handler.start_listener(connection_handler)

        while True:
            command, data = ChatProtocol.parse_push_message(connection_handler.do_listen(conn))
            if command == OK_STATUS:
                text_logger.write(data[0])
            elif command == MSG_COMMAND:
                text_logger.write(DATA_COLOR + f"got msg from {data[0]}:{PENDING_COLOR + f'{data[1]}'}")
            elif command == CLOSE_COMMAND:
                connection_handler.close_connection()
                text_logger.write("the server close the connection with the wconn")
                return
            else:
                text_logger.write("the server send an illegal command to wconn, shutting down the client!")
                connection_handler.close_connection()
                return
