import socket
import threading


class Server:
    def __init__(self, max_clients=5, port=5412):
        self.max_clients = max_clients
        self.port = port
        self.connected_clients = []
        self.lock = threading.Lock()  # Lock to ensure thread-safe access
        self.running = False  # Flag to see if server is running

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
            # Add new client socket to list on connected clients
            with self.lock:
                self.connected_clients.append(client_sock)
            print(f"Client connected: {addr}")

            # Start new thread to handle comms with this client
            threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()

    def handle_client(self, client_sock):
        while self.running:
            try:
                # Receive message form client
                msg = client_sock.recv(1024).decode('utf-8')
                if msg == "status":
                    # If client asks for status, respond with current connection
                    with self.lock:
                        status = f"{len(self.connected_clients)},{self.max_clients}"
                    client_sock.sendall(status.encode('utf-8'))
            except:
                break
