DELIMITER = "|"
LOGIN_COMMAND = "login"
CLOSE_COMMAND = "close"
CONNECTED_COMMAND = "connected"
AUTHORIZE_COMMAND = "authorize"
SEND_MESSAGE_COMMAND = "sendto"
WCONN_COMMAND = "wconn"
ENCRYPT_COMMAND = "start_enc"

MESSAGE_PREFIX = "msg"
CLOSE_PREFIX = "close"

OK_STATUS = "ok"

class ChatProtocol:
    @staticmethod
    def build_login(username, pwd):
        return f"{LOGIN_COMMAND}{DELIMITER}{username}{DELIMITER}{pwd}"

    @staticmethod
    def parse_response(data):
        return data.split(DELIMITER)

    @staticmethod
    def parse_push_message(data):
        return data.split(DELIMITER)[0], data.split(DELIMITER)[1:]

    @staticmethod
    def build_close_connection():
        return f"{CLOSE_COMMAND}{DELIMITER}"

    @staticmethod
    def build_get_connected_users():
        return f"{CONNECTED_COMMAND}{DELIMITER}"

    @staticmethod
    def build_authorize(username):
        return f"{AUTHORIZE_COMMAND}{DELIMITER}{username}"

    @staticmethod
    def build_send_message(target_user, msg):
        return f"{SEND_MESSAGE_COMMAND}{DELIMITER}{target_user}{DELIMITER}{msg}"

    @staticmethod
    def parse_send_message(data):
        return data.split(DELIMITER)

    @staticmethod
    def build_set_wconn(ip, port):
        return f"{WCONN_COMMAND}{DELIMITER}{ip}{DELIMITER}{port}"

    @staticmethod
    def parse_set_wconn(data):
        return data.split(DELIMITER)

    @staticmethod
    def build_start_encrypt():
        return f"{ENCRYPT_COMMAND}{DELIMITER}"

    @staticmethod
    def parse_start_encrypt(data):
        return data.split(DELIMITER)

