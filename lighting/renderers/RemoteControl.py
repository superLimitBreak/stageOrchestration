from libs.misc import parse_rgb_color, one_to_limit

from lighting import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class RemoteControl(AbstractDMXRenderer):
    """
    Using the lighting config data, control the dmx lights from a remote source
    using json display trigger events
    """
    __name__ = 'lights'

    def __init__(self, config):
        super().__init__()
        self.config = config

    def set(self, data):
        #print(data)
        device = data.get('device')
        value = data.get('value')
        try:
            # Device is integer - manipulate dmx index value directly
            self.dmx_universe[int(device)] = one_to_limit(float(value), limit=255)
        except ValueError:
            # Device is string - lookup/render alias
            self.config.render_device(self.dmx_universe, device, parse_rgb_color(value))

    def clear(self, *args, **kwargs):
        # This is really inefficent - Whats a better way?
        for i in range(len(self.dmx_universe)):
            self.dmx_universe[i] = 0