import argparse
import os
import socket
import threading
from datetime import datetime
from Storage import Storage


class Server:
    def __init__(self, address, port, stor_dir=None):
        self.ADDRESS = (address, port)
        self.readable = 1
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.commands = {'0': self._add,
                         '1': self._get,
                         '2': self._remove,
                         '3': self._check}
        self.connections = list()

        self.still_working = True
        self.storage = Storage() if stor_dir is None else Storage(stor_dir)
        self.log_dir = 'server_log'
        if not os.path.exists(self.log_dir):
            open(self.log_dir, 'w').close()

    def start(self):
        print("Starting server " + str(self.ADDRESS))
        with self.server as server:
            server.bind(self.ADDRESS)
            server.listen(socket.SOMAXCONN)

            while True:
                if not self.still_working:
                    break
                conn, address = server.accept()
                self._log("Got connection from {}".format(address))
                self.connections.append(conn)
                th = threading.Thread(target=lambda:
                self.handle_connection(conn, address))
                th.daemon = True
                th.start()
        self.storage.close()
        for conn in self.connections:
            conn.close()
        self._log('Server closed')

    def handle_connection(self, sock, address):
        while sock.fileno() != -1:
            data = sock.recv(11).decode('utf-8')
            if not data:
                self.connections.remove(sock)
                sock.close()
                continue
            key_lenght = int(data[1:])
            key = sock.recv(key_lenght).decode('utf-8')
            self.commands[data[0]](key, sock, address)
        self._log('Connection was closed', str(address))

    def _log(self, *args):
        with open(self.log_dir, 'a') as log:
            print(str(datetime.now()) + ' ' + ' '.join(args))
            log.write(str(datetime.now()) + ' ' + ' '.join(args) + '\n')

    def _add(self, key, sock: socket.socket, address):
        value_len = int(sock.recv(10).decode('utf-8'))
        value = sock.recv(value_len).decode('utf-8')
        while self.readable < 1:
            continue
        self.readable -= 1
        self._log(str(address), 'add', key, value)
        self.storage.add(key, value)
        self.readable += 1

    def _get(self, key, sock: socket.socket, address):
        value = self.storage.get(key)
        self._log(str(address), 'get', key, value)
        message = Server._get_lenght(value) + value
        sock.send(message.encode("utf-8"))

    def _remove(self, key, sock: socket.socket, address):
        self.storage.remove_key(key)
        self._log(str(address), 'rm', key)

    def _check(self, key, sock: socket.socket, address):
        sock.send('1111111111'.encode('utf-8'))
        self._log(str(address), 'ping')

    @staticmethod
    def _get_lenght(s: str):
        s_len = str(len(s))
        s_len = '0' * (10 - len(s_len)) + s_len
        return s_len


def createParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '-i', nargs='?', help='Server ip. Format: ip;port')
    parser.add_argument('-dir', '-d', nargs='?', help='DataBase directory')
    return parser


if __name__ == '__main__':
    from os.path import join, dirname
    parser = createParser()
    namespace = parser.parse_args()

    with open(join(dirname(__file__), 'server_config'), 'r') as conf:
        ip, port = conf.readline()[:-1].split(' ')
        directory = conf.readline()

    if namespace.ip is not None:
        ip, port = namespace.ip.split(';')
    if namespace.dir is not None:
        directory = namespace.dir

    if directory == '':
        server = Server(ip, int(port))
        server.start()
    else:
        server = Server(ip, int(port), directory)
        server.start()
