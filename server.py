import ast
import socket
import threading
from player import Player


class Server(Player):
    def __init__(self, max_clients=5, port=5412):
        super().__init__(self)
        self.max_clients = max_clients
        self.port = port
        self.lock = threading.Lock()  # Lock to ensure thread-safe
        self.running = False  # Flag to see if server is running
        self.start_game = False
        self.game_over = False
        self.signal_new_round = False
        self.all_bid = False
        self.num_rounds = 0
        self.round_starter = self
        self.current_player = None
        self.trump_card = None
        self.ready_statuses = [False]
        self.connected_clients = []
        self.player_bids = []
        self.client_hands = []
        self.played_cards = []
        self.play_order = []
        self.player_points = []
        self.cur_round = 0
        self.tricks_taken = []
        self.prevent_trick = False


    def start(self):
        self.running = True
        threading.Thread(target=self.listen_for_clients, daemon=True).start()

    def listen_for_clients(self):
        # Create socket and bind to listen on all networks
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(("0.0.0.0", self.port))

        # Make socket listen
        server_sock.listen(self.max_clients)
        print("Server is listening on port", self.port)

        # Loop to continuously accept new clients

        while self.running and len(self.connected_clients) < self.max_clients:
            client_sock, addr = server_sock.accept()
            with self.lock:
                self.connected_clients.append(client_sock)
                self.ready_statuses.append(False)
            print(f"Client connected: {addr}")

            # Start new thread to handle comms with this client
            threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()

    def handle_client(self, client_sock):
        while self.running:
            msg = client_sock.recv(1024).decode('utf-8').strip()
            if not msg:
                break

            if msg == "status":
                with self.lock:
                    response = f"{len(self.connected_clients)},{self.max_clients},{self.ready_statuses}"
                client_sock.sendall(response.encode('utf-8'))

            elif msg == "num_players?":
                with self.lock:
                    response = f"{len(self.connected_clients) + 1}"
                    client_sock.sendall(response.encode('utf-8'))

            elif msg == "ready":
                with self.lock:
                    index = self.connected_clients.index(client_sock)
                    self.ready_statuses[index + 1] = True  # Mark client ready
                    print(f"Client {index + 1} is ready")
                    print(self.ready_statuses)

            elif msg == "request_ready_states":
                with self.lock:
                    ready_states_str = ','.join(map(str, self.ready_statuses))
                    client_sock.sendall(f"update_ready_states:{ready_states_str}".encode('utf-8'))

            elif msg == "start_game?":
                with self.lock:
                    response = f"{self.start_game}"
                    client_sock.sendall(response.encode('utf-8'))

            elif msg == "player-bids?":
                with self.lock:
                    index = self.connected_clients.index(client_sock)
                    data = {
                        "player_bids": self.player_bids,
                        "tricks_taken": self.tricks_taken,
                        "points": self.player_points[index + 1]
                    }
                    client_sock.sendall(str(data).encode('utf-8'))

            elif msg == "bid?" or msg == "my-turn?":
                with self.lock:
                    if client_sock == self.current_player:
                        client_sock.sendall("yes".encode('utf-8'))
                    else:
                        client_sock.sendall("no".encode('utf-8'))

            elif msg == "points?":
                with self.lock:
                    client_idx = self.connected_clients.index(client_sock) + 1
                    client_sock.sendall(str(self.player_points[client_idx]).encode('utf-8'))

            elif msg == "new-round?":
                with self.lock:
                    if self.game_over:
                        self.handle_game_over()
                    elif self.signal_new_round:
                        client_sock.sendall("yes".encode('utf-8'))
                    else:
                        client_sock.sendall("no".encode('utf-8'))

            elif msg == "start-round":
                with self.lock:
                    index = self.connected_clients.index(client_sock)
                    data = {
                        "hand": self.client_hands[index],
                        "trump": (self.trump_card.ID, self.trump_card.suit),
                        "played_cards": self.played_cards
                    }
                    client_sock.sendall(str(data).encode('utf-8'))

            elif msg == "game-state":
                with self.lock:
                    index = self.connected_clients.index(client_sock)
                    state = {
                        "played_cards": self.played_cards,
                        "tricks_taken": self.tricks_taken,
                        "player_bids": self.player_bids,
                        "my_tricks": self.tricks_taken[index + 1],
                    }
                    response = str(state)
                    client_sock.sendall(response.encode('utf-8'))

            elif msg.startswith("new-played "):
                with self.lock:
                    card_str = msg[len("new-played "):].strip()
                    card = ast.literal_eval(card_str)
                    self.adjust_played_cards(card, client_sock)
                    client_index = self.connected_clients.index(self.current_player)
                    self.client_hands[client_index].remove(card)
                    self.next_player()

            elif msg.startswith("Bid is: "):
                with self.lock:
                    client_bid = int(msg[len("Bid is: "):])
                    index = self.connected_clients.index(client_sock)
                    self.player_bids[index + 1] = client_bid
                    self.next_player()
                    self.signal_new_round = False

        # Clean up if client disconnects -> Thread sync = with
        with self.lock:
            index = self.connected_clients.index(client_sock)
            self.connected_clients.pop(index)
            self.ready_statuses.pop(index + 1)  # Remove corresponding readiness status
        client_sock.close()

    def send_ready_states(self):
        with self.lock:
            # Broadcast the current ready states to all connected clients
            ready_states_str = ','.join(map(str, self.ready_statuses))
            for client_sock in self.connected_clients:
                client_sock.sendall(f"update_ready_states:{ready_states_str}".encode('utf-8'))

    def get_clients(self, index):
        with self.lock:
            if 0 <= index < len(self.connected_clients):
                return self.connected_clients[index]
            else:
                return None

    def initialize_hands(self):
        self.player_bids = [-1] * (len(self.connected_clients) + 1)
        self.client_hands = [-1] * len(self.connected_clients)
        self.tricks_taken = [0] * (len(self.connected_clients) + 1)
        all_players = [self] + self.connected_clients
        current_index = all_players.index(self.round_starter)
        next_index = (current_index + 1) % len(all_players)
        self.round_starter = all_players[next_index]
        self.current_player = self.round_starter
        self.signal_new_round = True

    def setup_hands(self, deck):
        with self.lock:
            for index, client in enumerate(self.connected_clients):
                if client in deck.hands:
                    hand_data = [(card.ID, card.suit) for card in deck.hands[client]]
                    self.client_hands[index] = hand_data

    def check_bids(self):
        if -1 in self.player_bids:
            self.all_bid = False
            return False
        else:
            self.all_bid = True
            self.current_player = self.round_starter
            return True

    def next_player(self):
        all_players = [self] + self.connected_clients
        current_index = all_players.index(self.current_player)
        next_index = (current_index + 1) % len(all_players)
        self.current_player = all_players[next_index]

    def check_all_went(self):
        return len(self.played_cards) == len([self] + self.connected_clients) and not self.prevent_trick

    def adjust_played_cards(self, new_card, player):
        if len(self.played_cards) + 1 > len([self] + self.connected_clients):
            self.played_cards = []
            self.play_order = []
            self.prevent_trick = False

        self.played_cards.append(new_card)
        self.play_order.append(player)

    def handle_game_over(self):
        max_points = max(self.player_points)
        max_idx = self.player_points.index(max_points) - 1
        if max_idx == -1:
            for c in self.connected_clients:
                c.sendall("lose".encode('utf-8'))

        else:
            for c in self.connected_clients:
                if c == self.connected_clients[max_idx]:
                    c.sendall("win".encode('utf-8'))
                else:
                    c.sendall("lose".encode('utf-8'))
