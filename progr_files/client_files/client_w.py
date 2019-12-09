import socket
import threading


class client_web:
    def __init__(self):
        self._connections = dict()
        self._freeze = False
        self.still_working = True
        self.ping_time = 0.1
        threading.Thread(target=self.check_connections).start()

    def send(self, message: str, address):
        while self._freeze:
            continue
        self._freeze = True
        conn = self.get_connection(address)
        if conn is None:
            self._freeze = False
            return
        try:
            conn.send(message.encode('utf-8'))
            self._freeze = False
            return True
        except ConnectionError:
            self._freeze = False
            self._connections.pop(address)
            print('Server ' + str(address) + ' is unreachable')

    def recieve(self, address):
        while self._freeze:
            continue
        self._freeze = True
        s = self.get_connection(address)
        if s is None:
            self._freeze = False
            return None
        try:
            value_len = s.recv(10).decode('utf-8')
            if value_len == '':
                raise ConnectionError()
            value_len = int(value_len)
            value = s.recv(value_len).decode('utf-8')
            self._freeze = False
            return value
        except ConnectionError:
            self._freeze = False
            self._connections.pop(address)
            print('Server ' + str(address) + ' is unreachable')
            return None

    def get_connection(self, address):
        if address in self._connections.keys():
            return self._connections[address]
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(address)
            self._connections[address] = s
            return s
        except ConnectionError:
            print('Server ' + str(address) + ' is unreachable')
            return None

    def check_connections(self):
        import time
        while self.still_working:
            while self._freeze:
                continue
            self._freeze = True
            connections = list(self._connections.items())
            for address, conn in connections:
                try:
                    conn.send('30000000000'.encode('utf-8'))
                    ans = conn.recv(10).decode('utf-8')
                    if ans != '1111111111':
                        self._connections.pop(address)
                except ConnectionError:
                    self._connections.pop(address)
                    print('Server ' + str(address) +
                          ' is unreachable for ping')
            self._freeze = False
            time.sleep(self.ping_time)

    def __del__(self):
        for addr, conn in self._connections.items():
            conn.close()
