class MessgeBuilder:
    @staticmethod
    def build_login(user, pwd):
        return f"login|{user}|{pwd}"

    @staticmethod
    def build_sendto_msg(target_user, msg):
        return f"sendto_msg|{target_user}|{msg}"

    @staticmethod
    def built_ok(msg=""):
        return f'ok|{msg}'

    def built_error(msg=""):
        return f'error|{msg}'

    @staticmethod
    def build_connected():
        return f"connected|"

    @staticmethod
    def build_authorize(target_user):
        return f"authorize|{target_user}"

    @staticmethod
    def build_close():
        return "close|"

    @staticmethod
    def build_start_enc():
        return "start_enc|"

    @staticmethod
    def build_wconn_enc():
        return "wconn_enc|"

    @staticmethod
    def build_msg(from_user, msg):
        return f"msg|{from_user}|{msg}"

    @staticmethod
    def build_backup(ip, port):
        return f"backup|{ip}|{port}"
