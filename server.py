import socket
import threading


class Server:
    def __init__(self, max_clients=5, port=5412):
        self.max_clients = max_clients
        self.port = port
        self.connected_clients = []
        self.lock = threading.Lock()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.listen_for_clients, daemon=True).start()

    def listen_for_clients(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(("0.0.0.0", self.port))
        server_sock.listen(self.max_clients)
        print("Server is listening on port", self.port)

        while self.running and len(self.connected_clients) < self.max_clients:
            client_sock, addr = server_sock.accept()
            with self.lock:
                self.connected_clients.append(client_sock)
            print(f"Client connected: {addr}")
            threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()

    def handle_client(self, client_sock):
        while self.running:
            try:
                msg = client_sock.recv(1024).decode('utf-8')
                if msg == "status":
                    with self.lock:
                        status = f"{len(self.connected_clients)},{self.max_clients}"
                    client_sock.sendall(status.encode('utf-8'))
            except:
                break
