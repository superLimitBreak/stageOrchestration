import logging
log = logging.getLogger(__name__)


class RealtimeOutputJSON(object):
    def __init__(self, device_collection, json_send_function):
        log.info('Init JSON Output')
        self.device_collection = device_collection
        self.json_send_function = json_send_function

    def update(self, frame):
        self.json_send_function(frame, _render_json(self.device_collection))


def _render_json(device_collection):
    return device_collection.todict()
