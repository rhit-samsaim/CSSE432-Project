import socket


class Client:
    def __init__(self, host):
        self.host = host
        self.port = 6539
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to server.")
            return True
        except Exception as e:
            print("Connection failed: {e}")
            return False