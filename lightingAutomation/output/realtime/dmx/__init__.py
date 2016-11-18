import logging

log = logging.getLogger(__name__)

from .ArtNet3 import ArtNet3

class RealtimeOutputDMX(object):
    def __init__(self, device_collection, dmx_host, dmx_mapping):
        log.info(f'Init DMX Output {dmx_host}')
        self.dmx_host = ArtNet3(dmx_host)
        self.dmx = bytearray()

    def update(self):
        self.dmx_host.dmx(self.render_dmx())

    def render_dmx(self):
        # With mapping, convert self.device_collection to dmx bytes

        return self.dmx
