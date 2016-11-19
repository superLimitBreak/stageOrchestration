import logging

log = logging.getLogger(__name__)

from .dmx import RealtimeOutputDMX
from .json import RealtimeOutputJSON


class RealtimeOutputManager(object):
    def __init__(self, device_collection, settings):
        self._output = {}

        # With settings init the required renderers
        if settings.get('dmx_host') and settings.get('dmx_mapping'):
            self._output['dmx'] = RealtimeOutputDMX(device_collection, settings['dmx_host'], settings['dmx_mapping'])
        if settings.get('json_send'):
            self._output['json'] = RealtimeOutputJSON(device_collection, settings['json_send'])

    def update(self):
        """
        Output the state of the device_collection to the registered output renderers
        """
        for output in self._output.values():
            output.update()
