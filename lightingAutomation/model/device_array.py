from copy import copy
from collections import OrderedDict

from pysistence import make_dict

from ext.attribute_packer import CollectionPackerMixin, BasePackerMixin

from .devices.rgb_light import RGBLight
from .devices.rgb_strip_light import RGBStripLight
from .devices.effect_light import EffectRGBLight
from .devices.smoke import Smoke
from .devices.dmx_passthrough import DMXPassthru


class DeviceCollection(CollectionPackerMixin):
    """
    A collection of lights with positions.
    This models the stage layout and devices
    """
    def __init__(self, devices):
        self._devices = make_dict(devices)
        self.groups = dict()
        CollectionPackerMixin.__init__(self, tuple(self._devices.values()))

    def get(self, name):
        pass
