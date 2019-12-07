import socket


class client_web:
    def __init__(self):
        self._connections = dict()
        self._freeze = False
        # threading.Thread(target=self.check_connections).start()

    def send(self, message: str, address):
        while self._freeze:
            continue
        conn = self.get_connection(address)
        if conn is None:
            return
        try:
            conn.send(message.encode('utf-8'))
            return True
        except ConnectionError:
            self._connections.pop(address)
            print('Server ' + str(address) + ' is unreachable')

    def recieve(self, address):
        while self._freeze:
            continue
        s = self.get_connection(address)
        if s is None:
            return None
        try:
            value_len = s.recv(10).decode('utf-8')
            value_len = int(value_len)
            value = s.recv(value_len).decode('utf-8')
            return value
        except ConnectionError:
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
        while True:
            self._freeze = True
            for address, conn in self._connections.items():
                try:
                    conn.send('30000000000'.encode('utf-8'))
                    ans = conn.recv(10).decode('utf-8')
                    if ans != '1111111111':
                        self._connections.pop(address)
                except ConnectionResetError or ConnectionAbortedError:
                    self._connections.pop(address)
                    # print('Server ' + str(address) + ' is unreachable')
            self._freeze = False
            time.sleep(10)

    def __del__(self):
        for addr, conn in self._connections.items():
            conn.close()
