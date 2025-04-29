import socket
import threading

class Server:
    def __init__(self, host='0.0.0.0'):
        self.host = host
        self.port = 6539
        self.max_clients = 6
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        print("Server started on {self.host}:{self.port}")

        #Start background thread (to prevent halting)
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while len(self.clients) < self.max_clients:
            client_socket, addr = self.server_socket.accept()
            print("Client connected from {addr}")
            self.clients.append(client_socket)
