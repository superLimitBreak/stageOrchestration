import logging

log = logging.getLogger(__name__)


class RealtimeOutputDMX(object):
    def __init__(self, device_collection, dmx_host, dmx_mapping):
        log.info(f'Init DMX Output {dmx_host}')
        import pdb ; pdb.set_trace()

    def update(self):
        pass
