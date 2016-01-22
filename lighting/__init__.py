import array
import os.path
import yaml
from collections import defaultdict

from libs.misc import file_scan, parse_rgb_color, one_byte_limit as limit

from lighting import devices

import logging
log = logging.getLogger(__name__)


DEFAULT_YAMLPATH = 'data'
DEFAULT_VERSION = '0.0.0'


def add_default_argparse_args(parser, version=DEFAULT_VERSION):
    parser.add_argument('--yamlpath', action='store', help='folder path for the yaml lighting data.', default=DEFAULT_YAMLPATH)
    parser.add_argument('--postmortem', action='store_true', help='enter debugger on exception')
    parser.add_argument('--log_level', type=int,  help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=version)



class AbstractDMXRenderer(object):
    DEFAULT_DMX_SIZE = 256

    @staticmethod
    def new_dmx_array(dmx_size=DEFAULT_DMX_SIZE, default_value=b'\x00'):
        dmx_universe = array.array('B')
        dmx_universe.frombytes(default_value*dmx_size)
        return dmx_universe

    def __init__(self, dmx_size=DEFAULT_DMX_SIZE):
        self.dmx_universe = self.new_dmx_array(dmx_size)

    def render(self, frame):
        """
        Given a frame number (that can be ignored)
        Return a dmx_universe byte array
        """
        #raise Exception('should override')
        return self.dmx_universe

    def close(self):
        #raise Exception('should override')
        pass


def mix(destination, sources, mix_func=max):
    for index, values in enumerate(zip(*sources)):
        destination[index] = mix_func(values)


def get_value_at(sequence, target, get_value_item_func):
    current = 0
    for index, item in enumerate(sequence):
        if not item:
            continue
        item_value = get_value_item_func(item)
        if target >= current and target < current + item_value:
            return item, target - current, index
        current += item_value
    return None, target - current, None


def open_yaml(path, target_class=None):
    with open(path, 'rb') as file_handle:
        obj_data = yaml.load(file_handle)
        return target_class(obj_data) if target_class else obj_data


def open_path(path, target_class=None):
    """
    Open all yamls in a path by constructing an object for each file based on the 'target' class
    """
    objs = {}
    for file_info in file_scan(path, r'.*\.yaml$'):
        objs[file_info.file_no_ext] = open_yaml(file_info.absolute, target_class)
    return objs


class LightingConfig(object):

    PATH_CONFIG_FILE = 'config.yaml'

    def __init__(self, yamlpath):
        self.config = open_yaml(os.path.join(yamlpath, self.PATH_CONFIG_FILE))
        self.device_lookup = defaultdict(list)

        def _generate_group_lookup(device):
            if device.get('type') == 'group':
                for group_item_device_name in device['group']:
                    for sub_device in _generate_group_lookup(self.config['devices'][group_item_device_name]):
                        yield sub_device
            else:
                yield device
        for name, device in self.config['devices'].items():
            self.device_lookup[name] += list(_generate_group_lookup(device))

    def normalize_rgbw(self, color_value):
        """
        Passthough color array
        >>> normalize_rgbw((1.0, 0, 0, 0))
        (1.0, 0, 0, 0)

        Get alias
        >>> normalize_rgbw('red')
        [1.0, 0, 0, 0]

        Parse color string
        >>> normalize_rgbw('1, 0, 0, 0')
        [1.0, 0, 0, 0]

        """
        return self.config['colors'].get(color_value, parse_rgb_color(color_value)) if isinstance(color_value, str) else color_value

    def color_calibration(self, device, rgbw):
        return getattr(devices, device.get('type'))(self.config, rgbw)

    def render_device(self, dmx, name, rgbw):
        if rgbw:
            rgbw = self.normalize_rgbw(rgbw)
        else:
            rgbw = (0, 0, 0, 0)

        def overlay(index, values):
            for offset, value in enumerate(values):
                dmx[index+offset] = limit(value)

        for device in self.device_lookup.get(name, ()):
            overlay(device['index'], self.color_calibration(device, rgbw))
