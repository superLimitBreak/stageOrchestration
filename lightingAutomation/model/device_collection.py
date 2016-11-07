from copy import copy
from collections import OrderedDict
from itertools import chain

from pysistence import make_dict

from ext.attribute_packer import CollectionPackerMixin, BasePackerMixin, MemoryFramePacker

from .devices.rgb_light import RGBLight
from .devices.rgb_strip_light import RGBStripLight
from .devices.effect_light import EffectRGBLight
from .devices.smoke import Smoke
from .devices.dmx_passthrough import DMXPassthru


class DeviceCollection(CollectionPackerMixin, MemoryFramePacker):
    """
    """
    def __init__(self, devices):
        self._devices = make_dict(devices)
        CollectionPackerMixin.__init__(self, tuple(self._devices.values()))
        MemoryFramePacker.__init__(self, self)
        self._device_lookup = {device_name: (device, ) for device_name, device in self._devices.items()}

    def add_group(self, group_name, device_names):
        self._device_lookup[group_name] = tuple(chain(*(
            self._device_lookup[device_name] for device_name in device_names
        )))

    def get_devices(self, name):
        return self._device_lookup.get(name, ())
