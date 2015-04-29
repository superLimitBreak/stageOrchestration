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

        self.thread = threading.Thread(target=self.recieve_loop, args=())
        self.thread.daemon = True

        self.running = False

    def listen(self):
        self.running = True
        self.thread.start()

    def recieve_loop(self):
        self.sock.bind((self.host, self.port))
        while self.running:
            data, addr = self.sock.recvfrom(self.buffer_size)
            self._recieve(addr, data)
        self.sock.shutdown(socket.SHUT_RDWR)

    def _recieve(self, addr, raw_data):
        print("received {0}: {1}".format(addr, raw_data))

    def _send(self, raw_data):
        self.sock.sendto(raw_data, (self.host, self.PORT))


from struct import Struct
from collections import namedtuple


class Datagram(object):
    OpCodeDefinition = namedtuple('OpCodeDefinition', ('name', 'opcode', 'fields', 'struct'))

    def __init__(self,  opcode_defenitions):
        self.lookup_opcode = {}
        self.lookup_namedtuple = {}
        self.lookup_struct = {}
        for opcode in opcode_defenitions:
            opcode_namedtuple = namedtuple(opcode.name, opcode.fields)
            self.lookup_opcode[opcode.opcode] = opcode_namedtuple
            self.lookup_opcode[opcode_namedtuple] = opcode.opcode
            self.lookup_namedtuple[opcode.name] = opcode_namedtuple
            self.lookup_struct[opcode_namedtuple] = Struct(opcode.struct)

    def get_namedtuple(self, index):
        if (isinstance(index, int)):
            return self.lookup_opcode[index]
        else:
            return self.lookup_namedtuple[index]

    def get_struct(self, opcode_namedtuple):
        return self.lookup_struct[opcode_namedtuple]

    def get_opcode(self, opcode_namedtuple):
        return self.lookup_opcode[opcode_namedtuple]

