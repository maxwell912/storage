from progr_files.Client import Client
from progr_files.Server import Server
from os.path import join
import os

IP = [("127.0.0.5", 8000), ("127.0.0.5", 8001), ("127.0.0.5", 8002), ("127.0.0.5", 8003)]
servers = list()


def test_smth():
    for i in range(len(IP)):
        os.mkdir(join(os.path.dirname(__file__), 'progr_files', 'DB', str(i)))
        server = Server(IP[i], join('progr_files', 'DB', str(i)))
        server.start()
        servers.append(server)

    client = Client(IP, 2)
    client.add(1, 1)
    client.add(2, 2)
    client.add(3, 3)
    client.add(4, 4)
    servers[0].stop()
    servers[1].stop()
    print(client.get(1))
    print(client.get(2))
    print(client.get(3))
    print(client.get(4))
    client.add(4, 4)
    print(client.get(4))
    servers[0].start()
    print(client.get(4))
    for server in servers:
        server.stop()
    import shutil
    for i in range(len(IP)):
        shutil.rmtree(join(os.path.dirname(__file__), 'progr_files', 'DB', str(i)))


if __name__ == '__main__':
    test_smth()
