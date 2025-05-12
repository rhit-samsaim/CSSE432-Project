from gameplay import create_host_game, create_client_game
from server import Server
from client import Client
from wizard_menu import main_menu
from lobby import create_lobby, create_client_lobby


def main():
    server_ip = main_menu()
    if server_ip == -1:
        run_as_host()
    else:
        run_as_client(server_ip)


def run_as_host():
    server = Server()
    server.start()
    create_lobby(server)
    create_host_game(server)


def run_as_client(ip):
    client = Client(ip)
    if client.connect():
        create_client_lobby(client)
    create_client_game(client)

if __name__ == "__main__":
    main()

