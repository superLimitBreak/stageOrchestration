from struct import Struct
from collections import namedtuple


class DMXDatagram(object):
    opcodes = {
        None: (namedtuple('Header', ['ID', 'OpCode', 'ProtVerHi', 'ProtVerLo']), Struct('8s<HBB')),
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
