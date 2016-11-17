import logging

log = logging.getLogger(__name__)


class RealtimeOutputManager(object):
    def __init__(self, device_collection, settings):
        self.device_collection = device_collection
        # With settings init the required renderers

    def output(self):
        log.debug('output')
