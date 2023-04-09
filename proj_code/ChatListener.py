from ChatProtocol import *

class ChatListener:

    @staticmethod
    def do_listen(connection_handler):
        conn = connection_handler.start_listener(connection_handler)

        while True:
            command, data = ChatProtocol.parse_push_message(connection_handler.do_listen(conn))
            if command == OK_STATUS:
                print(data[0])
            elif command == MESSAGE_PREFIX:
                print(f"got msg from {data[0]}: {data[1]}")
            elif command == CLOSE_PREFIX:
                connection_handler.close_connection()
                exit("the server close the connection with the wconn")
            else:
                print("the server send an illegal command to wconn, shutting down the client!")
                connection_handler.close_connection()
                exit()

