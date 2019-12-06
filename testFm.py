from progr_files.Client import Client
from progr_files.Server import Server
import threading

IP = [("127.0.0.5", 8000)] # , ("127.0.0.5", 8001)]
servers = list()

# for address in IP:
#     server = Server(*address)
#     servers.append(server)
#     th = threading.Thread(target=server.start)
#     th.start()


if __name__ == '__main__':
    import time
    server = Server("127.0.0.5", 8000)
    server.start()
    client = Client(IP)
    client.add(1, 1)
    print(client.get(1))
    server.stop()
    client.add(2, 2)
    print(client.get(2))
    server.start()
    print(client.get(1))
    server.stop()
