import hashlib
import socket
import argparse


class Client:
    Servers = list()
    Connections = dict()

    def add(self, key, value):
        key, value = str(key), str(value)
        key_len = Client._get_lenght(key)
        value_len = Client._get_lenght(value)
        if len(Client.Servers) > 0:
            storage = Client.choose_storage(key)
            message = '0' + key_len + key + value_len + value
            if Client.send(message, storage):
                print('Value added')
        else:
            raise Exception("Невозможно установить соединение.")

    def get(self, key):
        key = str(key)
        key_len = Client._get_lenght(key)
        if len(Client.Servers) > 0:
            message = '1' + key_len + key
            storage = Client.choose_storage(key)
            if Client.send(message, storage):
                return Client.recieve(storage)
            return None
        else:
            raise Exception("Невозможно установить соединение.")

    def remove(self, key):
        key = str(key)
        key_len = Client._get_lenght(key)
        if len(Client.Servers) > 0:
            message = '2' + key_len + key
            Client.send(message, Client.choose_storage(key))
        else:
            raise Exception("Нет доступных серверов")

    @staticmethod
    def send(message: str, address):
        connections = Client.Connections
        if Client.check_connection(address):
            connections[address].send(message.encode('utf-8'))
            return True
        return False

    @staticmethod
    def recieve(address):
        connections = Client.Connections
        s = connections[address]
        value_len = s.recv(10).decode('utf-8')
        value_len = int(value_len)
        value = s.recv(value_len).decode('utf-8')
        return value

    @staticmethod
    def get_connection(address):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(address)
            return s
        except Exception:
            print('Server ' + str(address) + ' is unreachable')
            return None

    @staticmethod
    def check_connection(address):
        connections = Client.Connections
        if address not in connections.keys() or connections[address].fileno() == -1:
            conn = Client.get_connection(address)
            if conn is None:
                return False
            connections[address] = conn
        conn = connections[address]
        try:
            conn.send('30000000000'.encode('utf-8'))
            ans = conn.recv(10).decode('utf-8')
            if ans == '1111111111':
                return True
        except Exception:
            Client.Connections.pop(address)
            print('Server ' + str(address) + ' is unreachable')
            return False

    @staticmethod
    def choose_storage(key):
        hash = Client._get_hash(key)
        length = len(Client.Servers)
        if len == 0:
            print('No servers available')
            return None
        return Client.Servers[hash % length]

    @staticmethod
    def _get_hash(string: str):
        hash = hashlib.md5(string.encode('utf-8')).hexdigest()
        return int(hash, 16) % 10 ^ 8

    @staticmethod
    def _get_lenght(s: str):
        s_len = str(len(s))
        s_len = '0' * (10 - len(s_len)) + s_len
        return s_len

    def __del__(self):
        for addr, conn in Client.Connections.items():
            conn.close()


def createParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '-i', nargs='*', help='Server ip. Format: ip;port')
    return parser


if __name__ == '__main__':
    from os.path import join, dirname
    from client_com import get_commands

    parser = createParser()
    namespace = parser.parse_args()
    client = Client()
    if namespace.ip is None or len(namespace.ip) == 0:
        with open(join(dirname(__file__), 'client_config'), 'r') as conf:
            for line in conf:
                address = line.split(' ')
                Client.Servers.append((address[0], int(address[1])))
    else:
        ips = namespace.ip
        try:
            for ip in ips:
                address = ip.split(';')
                Client.Servers.append((address[0], int(address[1])))
        except IndexError:
            raise Exception('Incorrect input')
    Client.Servers.sort()
    get_commands(client)
