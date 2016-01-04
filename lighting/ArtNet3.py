## -*- coding: utf-8 -*-
from libs.udp import UDPMixin, Datagram


class ArtNe3tDatagram(Datagram):
    """
    A datagram handler that matches the spec at a binary level.
    A separate layer should be implemented above this class to support more complex decoding and deriving fields:
      e.g. calculating the payload length field OR combining Lo/Hi tuple items to form a single coheran value
    """
    header_id = b'Art-Net\x00'
    header_ProtVer = 14

    opcode_definitions = (
        Datagram.OpCodeDefinition('Header', None, ('ID', 'OpCode', 'ProtVer'), '<8sHxB'),  # The ProtVer in the spec is a differnt endian to the OpCode - as the Hi byte is never used I've skipped the hi bype with 'xB' rather than 'H'
        Datagram.OpCodeDefinition('Poll', 0x2000, (), ''),
        Datagram.OpCodeDefinition('PollReply', 0x2100, (), ''),
        Datagram.OpCodeDefinition('DiagData', 0x2300, (), ''),
        Datagram.OpCodeDefinition('Command', 0x2400, (), ''),
        Datagram.OpCodeDefinition('Output', 0x5000, ('Sequence', 'Physical', 'SubUni', 'Net', 'Length'), '>BBBBH'),
        Datagram.OpCodeDefinition('Nzs', 0x5100, (), ''),
        Datagram.OpCodeDefinition('Address', 0x6000, (), ''),
        Datagram.OpCodeDefinition('Input', 0x7000, (), ''),
        Datagram.OpCodeDefinition('TodRequest', 0x8000, (), ''),
        Datagram.OpCodeDefinition('TodData', 0x8100, (), ''),
        Datagram.OpCodeDefinition('TodControl', 0x8200, (), ''),
        Datagram.OpCodeDefinition('Rdm', 0x8300, (), ''),
        Datagram.OpCodeDefinition('RdmSub', 0x8400, (), ''),
        Datagram.OpCodeDefinition('VideoSetup', 0xa010, (), ''),
        Datagram.OpCodeDefinition('VideoPalette', 0xa020, (), ''),
        Datagram.OpCodeDefinition('VideoData', 0xa040, (), ''),
        Datagram.OpCodeDefinition('MacMaster', 0xf000, (), ''),
        Datagram.OpCodeDefinition('MacSlave', 0xf100, (), ''),
        Datagram.OpCodeDefinition('FirmwareMaster', 0xf200, (), ''),
        Datagram.OpCodeDefinition('FirmwareReply', 0xf300, (), ''),
        Datagram.OpCodeDefinition('FileTnMaster', 0xf400, (), ''),
        Datagram.OpCodeDefinition('FileFnMaster', 0xf500, (), ''),
        Datagram.OpCodeDefinition('FileFnReply', 0xf600, (), ''),
        Datagram.OpCodeDefinition('IpProg', 0xf800, (), ''),
        Datagram.OpCodeDefinition('IpProgReply', 0xf900, (), ''),
        Datagram.OpCodeDefinition('Media', 0x9000, (), ''),
        Datagram.OpCodeDefinition('MediaPatch', 0x9100, (), ''),
        Datagram.OpCodeDefinition('MediaControl', 0x9200, (), ''),
        Datagram.OpCodeDefinition('MediaContrlReply', 0x9300, (), ''),
        Datagram.OpCodeDefinition('TimeCode', 0x9700, ('Frames', 'Seconds', 'Minutes', 'Hours', 'Type'), 'xxBBBBB'),
        Datagram.OpCodeDefinition('TimeSync', 0x9800, (), ''),
        Datagram.OpCodeDefinition('Trigger', 0x9900, (), ''),
        Datagram.OpCodeDefinition('Directory', 0x9a00, (), ''),
        Datagram.OpCodeDefinition('DirectoryReply', 0x9b00, (), ''),
    )

    def __init__(self):
        Datagram.__init__(self, ArtNe3tDatagram.opcode_definitions)

    def decode(self, raw_data):
        r"""
        >>> datagram = ArtNe3tDatagram()
        >>> datagram.decode(b'Art-Net\x00\x00\x97\x00\x0e\x00\x00\x18\x3C\x3C\x18\x00')
        (TimeCode(Frames=24, Seconds=60, Minutes=60, Hours=24, Type=0), b'')
        """
        # Decode Header
        header_namedtuple = self.get_namedtuple('Header')
        header_struct = self.get_struct(header_namedtuple)
        header_data = header_namedtuple._make(header_struct.unpack(raw_data[0:header_struct.size]))
        # Check Header
        assert header_data.ID == ArtNe3tDatagram.header_id
        assert header_data.ProtVer == ArtNe3tDatagram.header_ProtVer
        #assert header_data.ProtVerLo == ArtNe3tDatagram.header_ProtVerLo

        # Decode Structured Data (now we know what opcode is being performed)
        data_namedtuple = self.get_namedtuple(header_data.OpCode)
        data_struct = self.get_struct(data_namedtuple)
        data = data_namedtuple._make(data_struct.unpack(raw_data[header_struct.size:header_struct.size+data_struct.size]))

        return data, raw_data[header_struct.size + data_struct.size:]

    def encode(self, opcode_namedtuple_data, data=b''):
        r"""
        >>> datagram = ArtNe3tDatagram()
        >>> datagram.encode(datagram.get_namedtuple('TimeCode')(Frames=24, Seconds=60, Minutes=60, Hours=24, Type=0))
        b'Art-Net\x00\x00\x97\x00\x0e\x00\x00\x18<<\x18\x00'
        """
        opcode = self.get_opcode(opcode_namedtuple_data.__class__)
        data_struct = self.get_struct(opcode_namedtuple_data.__class__)

        # Encode Header
        header_namedtuple = self.get_namedtuple('Header')
        header_struct = self.get_struct(header_namedtuple)
        header_data = header_struct.pack(*header_namedtuple(
            ID=ArtNe3tDatagram.header_id,
            OpCode=opcode,
            ProtVer=ArtNe3tDatagram.header_ProtVer,
        ))

        # Encode Data
        payload_data = data_struct.pack(*opcode_namedtuple_data)

        return header_data + payload_data + data


class ArtNet3(UDPMixin):
    DATAGRAM = ArtNe3tDatagram()
    PORT = 0x1936

    def __init__(self, host=UDPMixin.DEFAULT_HOST):
        UDPMixin.__init__(self, host=host, port=ArtNet3.PORT)

    # Utils ------------

    def get_namedtuple(self, name):
        return self.DATAGRAM.get_namedtuple(name)

    # Recieve handling ----------

    def _recieve(self, addr, raw_data):
        r"""
        Called from UDPMixin with raw udp packet data

        >>> art3 = ArtNet3()
        >>> art3._recieve(None, b'Art-Net\x00\x00P\x00\x0e\x00\x00\x00\x00\x00\x04\x00\x01\x02\x03')
        b'\x00\x01\x02\x03'

        Todo: Disabled test, how do I check the assertion is raised? Do I need try:except:?
        >> art3._recieve(None, b'Art-Net\x00\x00P\x00\x0e\x00\x00\x00\x00\x00\x04\x00\x01\x02\x03\x04')
        AssertionError: Payload length should match length described in header
        """
        data, payload = self.DATAGRAM.decode(raw_data)
        if isinstance(data, self.get_namedtuple('Output')):
            assert data.Length == len(payload), "Payload length should match length described in header"
            self.recieve_dmx(payload)
        else:
            self.recieve(data, payload)

    def recieve(self, data, payload):
        """
        Override
        All messages (other than a dmx byte string) are collected here
        """
        print('received {0}: {1}'.format(data, payload))

    def recieve_dmx(self, data):
        """
        Override
        Reciving a dmx string is the primary use case for this class, so it has it's own default method
        """
        print(data)

    # Send handling ------

    def _dmx(self, data):
        r"""
        >>> art3 = ArtNet3()
        >>> art3._dmx(b'\x00\x01\x02\x03')
        b'Art-Net\x00\x00P\x00\x0e\x00\x00\x00\x00\x00\x04\x00\x01\x02\x03'
        """
        assert len(data) % 2 == 0, "data payload must be an even length"  # Todo: padd data to an even length automatically
        output_data = self.get_namedtuple('Output')(
            Sequence=0,
            Physical=0,
            SubUni=0,
            Net=0,
            Length=len(data)
        )
        return self.DATAGRAM.encode(output_data, data)

    def dmx(self, data):
        self._send(self._dmx(data))
