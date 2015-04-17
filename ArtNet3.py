## -*- coding: utf-8 -*-

from struct import Struct
from collections import namedtuple


class DMXDatagram(object):
    header_id = b'Art-Net\x00'
    opcodes = {
        None: (namedtuple('Header', ['ID', 'OpCode', 'ProtVerHi', 'ProtVerLo']), Struct('>8sHBB')),
        0x2000: (namedtuple('Poll', []), ''),
        0x2100: (namedtuple('PollReply', []), ''),
        0x2300: (namedtuple('DiagData', []), ''),
        0x2400: (namedtuple('Command', []), ''),
        0x5000: (namedtuple('Output', ['Sequence', 'Physical', 'SubUni', 'Net', 'LengthHi', 'Length', 'Data']), Struct('BBBBBB')),  # Special case with data
        0x5100: (namedtuple('Nzs', []), ''),
        0x6000: (namedtuple('Address', []), ''),
        0x7000: (namedtuple('Input', []), ''),
        0x8000: (namedtuple('TodRequest', []), ''),
        0x8100: (namedtuple('TodData', []), ''),
        0x8200: (namedtuple('TodControl', []), ''),
        0x8300: (namedtuple('Rdm', []), ''),
        0x8400: (namedtuple('RdmSub', []), ''),
        0xa010: (namedtuple('VideoSetup', []), ''),
        0xa020: (namedtuple('VideoPalette', []), ''),
        0xa040: (namedtuple('VideoData', []), ''),
        0xf000: (namedtuple('MacMaster', []), ''),
        0xf100: (namedtuple('MacSlave', []), ''),
        0xf200: (namedtuple('FirmwareMaster', []), ''),
        0xf300: (namedtuple('FirmwareReply', []), ''),
        0xf400: (namedtuple('FileTnMaster', []), ''),
        0xf500: (namedtuple('FileFnMaster', []), ''),
        0xf600: (namedtuple('FileFnReply', []), ''),
        0xf800: (namedtuple('IpProg', []), ''),
        0xf900: (namedtuple('IpProgReply', []), ''),
        0x9000: (namedtuple('Media', []), ''),
        0x9100: (namedtuple('MediaPatch', []), ''),
        0x9200: (namedtuple('MediaControl', []), ''),
        0x9300: (namedtuple('MediaContrlReply', []), ''),
        0x9700: (namedtuple('TimeCode', ['Frames', 'Seconds', 'Minutes', 'Hours', 'Type']), Struct('xxBBBBB')),
        0x9800: (namedtuple('TimeSync', []), ''),
        0x9900: (namedtuple('Trigger', []), ''),
        0x9a00: (namedtuple('Directory', []), ''),
        0x9b00: (namedtuple('DirectoryReply', []), ''),
    }

    @staticmethod
    def decode(raw_data):
        r"""
        >>> DMXDatagram.decode(b'Art-Net\x00\x97\x00\x01\x04\x00\x00\x18\x3C\x3C\x18\x00')
        (TimeCode(Frames=24, Seconds=60, Minutes=60, Hours=24, Type=0), b'')
        """
        header_structure, header_struct = DMXDatagram.opcodes[None]
        header_data = header_structure._make(header_struct.unpack(raw_data[0:header_struct.size]))
        assert header_data.ID == DMXDatagram.header_id
        data_structure, data_struct = DMXDatagram.opcodes[header_data.OpCode]
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


