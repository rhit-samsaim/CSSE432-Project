import socket
import threading


class Server:
    def __init__(self, max_clients=5, port=5412):
        self.max_clients = max_clients
        self.port = port
        self.connected_clients = []
        self.lock = threading.Lock()  # Lock to ensure thread-safe
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
            with self.lock:
                self.connected_clients.append(client_sock)
            print(f"Client connected: {addr}")

            # Start new thread to handle comms with this client
            threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()

    def handle_client(self, client_sock):
        while self.running:
            try:
                msg = client_sock.recv(1024).decode('utf-8').strip()
                if not msg:
                    break

                if msg == "status":
                    with self.lock:
                        count = len(self.connected_clients)
                        readiness_flags = [str(int(ready)) for (_, ready) in self.connected_clients]
                        response = f"{count},{self.max_clients}," + ",".join(readiness_flags)
                    client_sock.sendall(response.encode('utf-8'))

                elif msg == "ready":
                    with self.lock:
                        for i, (sock, ready) in enumerate(self.connected_clients):
                            if sock == client_sock:
                                self.connected_clients[i] = (sock, True)
                                print("Client marked as ready")
                                break
            except:
                break

        # Clean up if client disconnects
        with self.lock:
            self.connected_clients = [(sock, ready) for (sock, ready) in self.connected_clients if sock != client_sock]
        client_sock.close()

    def get_clients(self, index):
        with self.lock:
            return self.connected_clients[index][0]  # only return socket