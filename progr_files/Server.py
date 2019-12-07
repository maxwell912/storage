import argparse
import os
import socket
import threading
from os.path import join, dirname
from datetime import datetime
from progr_files.server_files.Storage import Storage

server_dir = dirname(__file__)


class Server:
    def __init__(self, address=None, stor_dr=None,
                 log_dir=join(server_dir, 'server_files',
                              'server_log'),
                 conf_dir=join(server_dir, 'server_files',
                               'server_config')):
        self._log_dir = log_dir
        self._conf_dir = conf_dir
        conf = self._load_conf()
        self.ADDRESS = (conf[0], conf[1]) if address is None else address
        self._readable = 1
        self._still_working = True

        self.server = None
        self.connections = dict()
        self._commands = {'0': self._add,
                          '1': self._get,
                          '2': self._remove,
                          '3': self._check}

        if stor_dr is None and conf[2] != '':
            stor_dr = conf[2]
        self.storage = Storage() if stor_dr is None else Storage(stor_dr)

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
        if self.server is not None:
            self.server.close()
            self._log('Server closed', str(self.ADDRESS))

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
            print(' '.join((str(datetime.now()),
                            str(self.ADDRESS)) + args))
            log.write(' '.join((str(datetime.now()),
                               str(self.ADDRESS)) + args) + '\n')

    def _add(self, key, sock: socket.socket, address):
        value_len = int(sock.recv(10).decode('utf-8'))
        value = sock.recv(value_len).decode('utf-8')
        while self._readable < 1:
            continue
        self._readable -= 1
        self._log(str(address), 'add',
                  'key:', key, 'value:', value)
        self.storage.add(key, value)
        self._readable += 1
        sock.send('00000000011'.encode('utf-8'))

    def _get(self, key, sock: socket.socket, address):
        value = self.storage.get(key)
        self._log(str(address), 'get',
                  'key:', key, 'value:', value)
        message = Server._get_lenght(value) + value
        sock.send(message.encode("utf-8"))

    def _remove(self, key, sock: socket.socket, address):
        self.storage.remove_key(key)
        self._log(str(address), 'rm', 'key:', key)
        sock.send('00000000011'.encode('utf-8'))

    def _check(self, key, sock: socket.socket, address):
        sock.send('1111111111'.encode('utf-8'))
        self._log(str(address), 'ping')

    def _load_conf(self):
        with open(self._conf_dir, 'r') as conf:
            ip, port = conf.readline()[:-1].split(' ')
            directory = conf.readline()
        return ip, int(port), directory

    @staticmethod
    def _get_lenght(s: str):
        s_len = str(len(s))
        s_len = '0' * (10 - len(s_len)) + s_len
        return s_len


def create_parser() -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-ip', '-i', nargs='?',
                            help='Server ip. Format: ip;port')
    arg_parser.add_argument('-dir', '-d', nargs='?',
                            help='DataBase directory')
    return arg_parser


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()

    address = None
    directory = None

    if namespace.ip is not None:
        address = namespace.ip.split(';')
    if namespace.dir is not None:
        directory = namespace.dir

    if address is not None:
        server = Server((address[0], int(address[1])), directory)
        server.start()
    else:
        server = Server(stor_dr=directory)
        server.start()
