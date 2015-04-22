## -*- coding: utf-8 -*-

from struct import Struct
from collections import namedtuple

OpCode = namedtuple('OpCode', ('name', 'opcode', 'fields', 'struct'))
opcode_definitions = (
    OpCode('Header', None, ('ID', 'OpCode', 'ProtVerHi', 'ProtVerLo'), '>8sHBB'),
    OpCode('Poll', 0x2000, (), ''),
    OpCode('PollReply', 0x2100, (), ''),
    OpCode('DiagData', 0x2300, (), ''),
    OpCode('Command', 0x2400, (), ''),
    OpCode('Output', 0x5000, ('Sequence', 'Physical', 'SubUni', 'Net', 'LengthHi', 'Length', 'Data'), 'BBBBBB'),
    OpCode('Nzs', 0x5100, (), ''),
    OpCode('Address', 0x6000, (), ''),
    OpCode('Input', 0x7000, (), ''),
    OpCode('TodRequest', 0x8000, (), ''),
    OpCode('TodData', 0x8100, (), ''),
    OpCode('TodControl', 0x8200, (), ''),
    OpCode('Rdm', 0x8300, (), ''),
    OpCode('RdmSub', 0x8400, (), ''),
    OpCode('VideoSetup', 0xa010, (), ''),
    OpCode('VideoPalette', 0xa020, (), ''),
    OpCode('VideoData', 0xa040, (), ''),
    OpCode('MacMaster', 0xf000, (), ''),
    OpCode('MacSlave', 0xf100, (), ''),
    OpCode('FirmwareMaster', 0xf200, (), ''),
    OpCode('FirmwareReply', 0xf300, (), ''),
    OpCode('FileTnMaster', 0xf400, (), ''),
    OpCode('FileFnMaster', 0xf500, (), ''),
    OpCode('FileFnReply', 0xf600, (), ''),
    OpCode('IpProg', 0xf800, (), ''),
    OpCode('IpProgReply', 0xf900, (), ''),
    OpCode('Media', 0x9000, (), ''),
    OpCode('MediaPatch', 0x9100, (), ''),
    OpCode('MediaControl', 0x9200, (), ''),
    OpCode('MediaContrlReply', 0x9300, (), ''),
    OpCode('TimeCode', 0x9700, ('Frames', 'Seconds', 'Minutes', 'Hours', 'Type'), 'xxBBBBB'),
    OpCode('TimeSync', 0x9800, (), ''),
    OpCode('Trigger', 0x9900, (), ''),
    OpCode('Directory', 0x9a00, (), ''),
    OpCode('DirectoryReply', 0x9b00, (), ''),
)

class DMXDatagram(object):
    header_id = b'Art-Net\x00'
    lookup_opcodes = {}
    lookup_op = {}

    @staticmethod
    def _init_opcodes(opcode_defenitions):
        for opcode in opcode_defenitions:
            DMXDatagram.lookup_opcodes[opcode.opcode] = (namedtuple(opcode.name, opcode.fields), Struct(opcode.struct))  #(namedtuple('Header', ), Struct()),
            #DMXDatagram.lookup_op[opcode.name] = opcode

    @staticmethod
    def decode(raw_data):
        r"""
        >>> DMXDatagram._init_opcodes(opcode_definitions)
        >>> DMXDatagram.decode(b'Art-Net\x00\x97\x00\x01\x04\x00\x00\x18\x3C\x3C\x18\x00')
        (TimeCode(Frames=24, Seconds=60, Minutes=60, Hours=24, Type=0), b'')
        """
        header_structure, header_struct = DMXDatagram.lookup_opcodes[None]
        header_data = header_structure._make(header_struct.unpack(raw_data[0:header_struct.size]))
        assert header_data.ID == DMXDatagram.header_id
        data_structure, data_struct = DMXDatagram.lookup_opcodes[header_data.OpCode]
        data = data_structure._make(data_struct.unpack(raw_data[header_struct.size:]))
        return data, raw_data[header_struct.size + data_struct.size:]

#import traceback
#import pdb
#import sys
#try:
#    print(DMXDatagram.decode(b'Art-Net\x00\x97\x00\x01\x04\x00\x00\x18\x3C\x3C\x18\x00'))
#except:
#    type, value, tb = sys.exc_info()
#    traceback.print_exc()
#    pdb.post_mortem(tb)


