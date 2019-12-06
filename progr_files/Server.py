import argparse
import os
import socket
import threading
from os.path import join, dirname
from datetime import datetime
from progr_files.server_files.Storage import Storage

server_dir = dirname(__file__)


class Server:
    def __init__(self, address, port, stor_dir=None):
        self.ADDRESS = (address, port)
        self._readable = 1
        self.server = None
        self._commands = {'0': self._add,
                          '1': self._get,
                          '2': self._remove,
                          '3': self._check}
        self.connections = dict()

        self._still_working = True
        self.storage = Storage() if stor_dir is None else Storage(stor_dir)
        self._log_dir = join(server_dir, 'server_files', 'server_log')

    def start(self):
        print("Starting server " + str(self.ADDRESS))
        self._still_working = True
        if not os.path.exists(self._log_dir):
            open(self._log_dir, 'w').close()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(self.ADDRESS)
        self.server.listen(socket.SOMAXCONN)
        threading.Thread(target=self.working).start()

    def working(self):
        while self._still_working:
            try:
                conn, address = self.server.accept()
            except OSError:
                return
            self._log("Got connection from {}".format(address))
            self.connections[address] = [conn, 0]
            th = threading.Thread(target=lambda:
                                  self.handle_connection(conn, address))
            th.daemon = True
            th.start()

    def stop(self):
        self._still_working = False
        self.storage.close()
        while True:
            if len(self.connections.keys()) == 0:
                break
            connections = list(self.connections.items())
            for address, conn in connections:
                if conn[1] == 0:
                    if address in self.connections.keys():
                        self.connections.pop(address)
                    conn[0].close()
        self.server.close()
        self._log('Server closed ' + str(self.ADDRESS))

    def handle_connection(self, sock, address):
        while self._still_working:
            try:
                data = sock.recv(11).decode('utf-8')
            except ConnectionAbortedError:
                data = ''
            if not data:
                if address in self.connections.keys():
                    self.connections.pop(address)
                sock.close()
                break
            self.connections[address][1] = 1
            key_lenght = int(data[1:])
            key = sock.recv(key_lenght).decode('utf-8')
            self._commands[data[0]](key, sock, address)
            self.connections[address][1] = 0
        self._log('Connection was closed', str(address))

    def _log(self, *args):
        with open(self._log_dir, 'a') as log:
            print(' '.join((str(datetime.now()), str(self.ADDRESS)) + args))
            log.write(str(datetime.now()) + ' ' + ' '.join(args) + '\n')

    def _add(self, key, sock: socket.socket, address):
        value_len = int(sock.recv(10).decode('utf-8'))
        value = sock.recv(value_len).decode('utf-8')
        while self._readable < 1:
            continue
        self._readable -= 1
        self._log(str(address), 'add', key, value)
        self.storage.add(key, value)
        self._readable += 1
        sock.send('00000000011'.encode('utf-8'))

    def _get(self, key, sock: socket.socket, address):
        value = self.storage.get(key)
        self._log(str(address), 'get', key, value)
        message = Server._get_lenght(value) + value
        sock.send(message.encode("utf-8"))

    def _remove(self, key, sock: socket.socket, address):
        self.storage.remove_key(key)
        self._log(str(address), 'rm', key)
        sock.send('00000000011'.encode('utf-8'))

    def _check(self, key, sock: socket.socket, address):
        sock.send('1111111111'.encode('utf-8'))
        self._log(str(address), 'ping')

    @staticmethod
    def _get_lenght(s: str):
        s_len = str(len(s))
        s_len = '0' * (10 - len(s_len)) + s_len
        return s_len


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '-i', nargs='?',
                        help='Server ip. Format: ip;port')
    parser.add_argument('-dir', '-d', nargs='?',
                        help='DataBase directory')
    return parser


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()

    with open(join(server_dir, 'server_config'), 'r') as conf:
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
