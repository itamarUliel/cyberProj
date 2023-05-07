class ReconnectBackupException(BaseException):
    def __init__(self):
        self.message = "prime is down, need to start over"

    def __str__(self):
        return f"ReconnectBackupException: {self.message}"

class HasNoBackupException(BaseException):
    def __init__(self):
        self.message = "there is no backup to connect"

    def __str__(self):
        return f"HasNoBackupException: {self.message}"
