DELIMITER = "|"
LOGIN_COMMAND = "login"
CLOSE_COMMAND = "close"
CONNECTED_COMMAND = "connected"
AUTHORIZE_COMMAND = "authorize"
SEND_MESSAGE_COMMAND = "sendto"
WCONN_COMMAND = "wconn"
ENCRYPT_COMMAND = "start_enc"
MSG_COMMAND = 'msg'
BACKUP_COMMAND = 'backup'
START_ENCRYPT_COMMAND = "start_enc"

OK_STATUS = "ok"
ERROR_STATUS = "error"

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
    def build_ok(msg=""):
        return f'{OK_STATUS}|{msg}'

    @staticmethod
    def build_error(msg=""):
        return f'{ERROR_STATUS}|{msg}'

    @staticmethod
    def parse_command(msg):
        return msg.split(DELIMITER)[0], msg.split(DELIMITER)[1:]

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

    @staticmethod
    def build_msg(from_user, msg):
        return f"{MSG_COMMAND}|{from_user}|{msg}"

    @staticmethod
    def build_backup(ip, port):
        return f"{BACKUP_COMMAND}|{ip}|{port}"

    @staticmethod
    def load_backup(data): # data = b"us1:a1,a2,a3|us2..."
        backup = {}
        for user in data.split(DELIMITER):
            if user == "":
                continue
            us, authorize_list = user.split(":")[0], user.split(":")[1].split(",")
            backup[us] = authorize_list
        return backup

    @staticmethod
    def build_error_message(msg=""):
        return [ERROR_STATUS, msg]

    @staticmethod
    def build_ok_message(msg=""):
        return [OK_STATUS, msg]

    @staticmethod
    def is_ok_status(msg):
        return msg[0] == "ok"
