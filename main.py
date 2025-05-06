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
    while True:
        print("Temp to keep server up")


def run_as_client(ip):
    client = Client(ip)
    if client.connect():
        create_client_lobby(client)

if __name__ == "__main__":
    main()

