import socket


class Client:
    def __init__(self, host):
        self.host = host
        self.port = 5411
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hand = []
        self.played_cards = []
        self.tricks_taken = []
        self.my_tricks = 0

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            print("Connected to server.")
            return True
        except Exception as e:
            print("Connection failed: {e}")
            return False

    def send(self, message):
        try:
            self.client_socket.sendall(message.encode('utf-8'))
        except:
            # print("Send failed")
            return

    def receive(self):
        try:
            return self.client_socket.recv(1024).decode('utf-8')
        except:
            print("Receive failed")
            return ""

    def handle_ready_states(self):
        while True:
            message = self.receive()
            if message.startswith("update_ready_states:"):
                ready_states = message[len("update_ready_states:"):].split(',')
                print("Updated Ready States:", ready_states)
                return ready_states
