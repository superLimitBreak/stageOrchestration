import array
import os.path
import yaml
from collections import defaultdict

from libs.misc import file_scan, parse_rgb_color, one_byte_limit as limit


import logging
log = logging.getLogger(__name__)


class AbstractDMXRenderer(object):
    DEFAULT_DMX_SIZE = 146

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

    def render_device(self, dmx, name, rgbw):
        if rgbw:
            rgbw = self.normalize_rgbw(rgbw)
        else:
            rgbw = (0, 0, 0, 0)

        for device in self.device_lookup.get(name, ()):
            i = device['index']
            if device.get('type') == 'lightRGBW':
                dmx[i+0] = limit(rgbw[0] * self.config['device_config']['lightRGBW']['red_factor'])
                dmx[i+1] = limit(rgbw[1] * self.config['device_config']['lightRGBW']['green_factor'])
                dmx[i+2] = limit(rgbw[2] * self.config['device_config']['lightRGBW']['blue_factor'])
                dmx[i+3] = limit(rgbw[3])
                #for index, value in enumerate(get_color_rgbw(color_value)):
                #    dmx[index+i] = limit(value)
            if device.get('type') == 'neoneonfloor':
                dmx[i] = self.config['device_config']['neoneonfloor']['mode']  # Constant to enter 3 light mode
                dmx[i+2] = limit(rgbw[0]+rgbw[3])
                dmx[i+3] = limit(rgbw[1]+rgbw[3])
                dmx[i+4] = limit(rgbw[2]+rgbw[3])
            if device.get('type') == 'neoneonfloorPart':
                dmx[i+0] = limit(rgbw[0]+rgbw[3])
                dmx[i+1] = limit(rgbw[1]+rgbw[3])
                dmx[i+2] = limit(rgbw[2]+rgbw[3])
            if device.get('type') == 'OrionLinkV2':
                dmx[i+0] = limit((rgbw[0]+rgbw[3]) * self.config['device_config']['lightRGBW']['red_factor'])
                dmx[i+1] = limit((rgbw[1]+rgbw[3]) * self.config['device_config']['lightRGBW']['green_factor'])
                dmx[i+2] = limit((rgbw[2]+rgbw[3]) * self.config['device_config']['lightRGBW']['blue_factor'])
            if device.get('type') == 'OrionLinkV2Final':
                dmx[i+0] = limit((rgbw[0]+rgbw[3]) * self.config['device_config']['lightRGBW']['red_factor'])
                dmx[i+1] = limit((rgbw[1]+rgbw[3]) * self.config['device_config']['lightRGBW']['green_factor'])
                dmx[i+2] = limit((rgbw[2]+rgbw[3]) * self.config['device_config']['lightRGBW']['blue_factor'])
                dmx[i+3] = 0  # No flash
                dmx[i+4] = 255  # Master dim
