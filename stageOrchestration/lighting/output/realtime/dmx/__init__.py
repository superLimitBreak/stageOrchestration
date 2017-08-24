import logging

import yaml
from pysistence import make_dict

from .ArtNet3 import ArtNet3

from . import dmx_devices

log = logging.getLogger(__name__)


class RealtimeOutputDMX(object):
    def __init__(self, host='localhost', mapping_config=None):
        log.info(f'Init DMX Output {host}')
        self.artnet = ArtNet3(host)
        with open(mapping_config, 'rt') as filehandle:
            self.mapping = make_dict(yaml.load(filehandle))
        self.buffer = bytearray(self.mapping.get('dmx_size', 512))

    def send(self, device_collection):
        self.artnet.dmx(self._render_dmx(device_collection, self.mapping, self.buffer))

    @staticmethod
    def _render_dmx(device_collection, mapping, buffer):
        """
        With mapping, convert device_collection to dmx bytes
        """
        for device_name, device in device_collection._devices.items():
            dmx_device_type, dmx_index = (mapping[device_name][attribute] for attribute in ('type', 'index'))
            dmx_bytes = getattr(dmx_devices, dmx_device_type)(device)
            buffer[dmx_index:dmx_index+len(dmx_bytes)] = dmx_bytes
        return buffer
