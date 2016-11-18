import logging

log = logging.getLogger(__name__)

from .dmx import RealtimeOutputDMX


class RealtimeOutputManager(object):
    def __init__(self, device_collection, settings):
        #self.device_collection = device_collection

        self._output = {}

        # With settings init the required renderers
        if settings.get('dmx_host') and settings.get('dmx_mapping'):
            self._output['dmx'] = RealtimeOutputDMX(device_collection, settings['dmx_host'], settings['dmx_mapping'])

    def update(self):
        """
        Output the state of the device_collection to the registered output renderers
        """
        for output in self._output.values():
            output.update()
