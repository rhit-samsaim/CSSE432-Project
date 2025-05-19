import ast
import socket
from player import Player


class Client(Player):
    def __init__(self, host):
        super().__init__(self)
        self.host = host
        self.port = 5412
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tricks_taken = []
        self.player_bids = []
        self.points = 0

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

    def get_client_game_info(self):
        self.send("game-state")
        data = ast.literal_eval(self.receive())
        self.played_cards = data["played_cards"]
        self.tricks_taken = data["tricks_taken"]
        self.my_tricks = data["my_tricks"]
        self.player_bids = data["player_bids"]

        self.send("my-turn?")
        return self.receive()
