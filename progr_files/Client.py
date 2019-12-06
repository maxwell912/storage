import hashlib
import argparse
from os.path import dirname, join
from progr_files.client_files.client_w import client_web


class Client:
    def __init__(self, servers: list = None, copy_count: int = 1,
                 conf_dir=join(dirname(__file__),
                               'client_files', 'client_config')):
        self._conn = client_web()
        self._conf_dir = conf_dir
        self._servers = self._load_conf() if servers is None else servers
        self._copy_count = min(copy_count, len(self._servers))
        if len(self._servers) == 0:
            raise Exception("Number of servers is 0")

    def add(self, key, value):
        key, value = str(key), str(value)
        key_len = Client._get_lenght(key)
        value_len = Client._get_lenght(value)
        message = '0' + key_len + key + value_len + value
        print('add ' + key + ' ' + value)

        storages = self.choose_storage(key)
        for storage in storages:
            self._conn.send(message, storage)
            if self._conn.recieve(storage) == '1':
                print('Value added ' + str(storage))

    def get(self, key):
        key = str(key)
        key_len = Client._get_lenght(key)
        message = '1' + key_len + key
        print('get ' + key)
        for storage in self.choose_storage(key):
            self._conn.send(message, storage)
            value = self._conn.recieve(storage)
            if value is not None:
                return value
        return None

    def remove(self, key):
        key = str(key)
        key_len = Client._get_lenght(key)
        message = '2' + key_len + key
        print('rm ' + key)
        for storage in self.choose_storage(key):
            self._conn.send(message, storage)
            if self._conn.recieve(storage) == '1':
                print('Key removed ' + str(storage))

    def choose_storage(self, key) -> list:
        hash = Client._get_hash(key)
        length = len(self._servers)
        servers = list()
        for i in range(self._copy_count):
            servers.append(self._servers[(hash + i) % length])
        return servers

    @staticmethod
    def _get_hash(string: str):
        hash = hashlib.md5(string.encode('utf-8')).hexdigest()
        return int(hash, 16) % 10 ^ 8

    @staticmethod
    def _get_lenght(s: str):
        s_len = str(len(s))
        s_len = '0' * (10 - len(s_len)) + s_len
        return s_len

    def _load_conf(self) -> list:
        servers = list()
        with open(self._conf_dir, 'r') as conf:
            for line in conf:
                address = line.split(' ')
                servers.append((address[0], int(address[1])))
        return servers


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '-i', nargs='*',
                        help='Server ip. Format: ip;port')
    parser.add_argument('-n', '-n', nargs='?',
                        help='Count of data copies in storage.')
    return parser


if __name__ == '__main__':
    from os.path import join, dirname
    from progr_files.client_files.client_com import get_commands

    parser = create_parser()
    namespace = parser.parse_args()
    servers = list()
    if namespace.ip is not None and len(namespace.ip) > 0:
        ips = namespace.ip
        try:
            for ip in ips:
                address = ip.split(';')
                servers.append((address[0], int(address[1])))
        except IndexError:
            raise Exception('Incorrect input')
    if len(servers) > 0:
        client = Client(servers, int(namespace.n))
    else:
        client = Client(copy_count=int(namespace.n))
    get_commands(client)
