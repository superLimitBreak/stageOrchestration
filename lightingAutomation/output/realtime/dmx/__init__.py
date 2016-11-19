import logging

import yaml
from pysistence import make_dict

from .ArtNet3 import ArtNet3

from . import dmx_devices

log = logging.getLogger(__name__)


class RealtimeOutputDMX(object):
    def __init__(self, device_collection, dmx_host, dmx_mapping):
        log.info(f'Init DMX Output {dmx_host}')
        self.device_collection = device_collection
        self.artnet = ArtNet3(dmx_host)
        with open(dmx_mapping, 'rt') as filehandle:
            self.mapping = make_dict(yaml.load(filehandle))
        self.dmx = bytearray(self.mapping.get('dmx_size', 512))

    def update(self):
        self.artnet.dmx(self.render_dmx())

    def render_dmx(self):
        """
        With mapping, convert self.device_collection to dmx bytes
        """
        for device_name, device in device_collection._devices.items():
            dmx_device_type, dmx_index = (self.mapping[device_name][attribute] for key in ('type', 'index'))
            dmx_bytes = getattr(dmx_devices, dmx_device_type)(device)
            self.dmx[dmx_index:dmx_index+len(dmx_bytes)] = dmx_bytes
        return self.dmx
