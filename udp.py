import socket
import threading


class UDPMixin(object):
    DEFAULT_BUFFER_SIZE = 1024
    DEFAULT_PORT = 5005

    def __init__(self, host='127.0.0.1', port=DEFAULT_PORT, buffer_size=DEFAULT_BUFFER_SIZE):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))

        self.thread = threading.Thread(target=self.recieve_loop, args=())
        self.thread.daemon = True

        self.running = True

    def listen(self):
        self.thread.start()

    def recieve_loop(self):
        while self.running:
            data, addr = self.sock.recvfrom(self.BUFFER_SIZE)
            self._recieve(addr, data)

    def _recieve(self, addr, raw_data):
        print("received {0}: {1}".format(addr, raw_data))

    def _send(self, raw_data):
        self.sock.sendto(raw_data, (self.host, self.PORT))
