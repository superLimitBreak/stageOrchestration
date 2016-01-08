from libs.misc import parse_rgb_color

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
        #import pdb; pdb.set_trace()
        self.config.render_device(
            self.dmx_universe,
            data.get('device'),
            parse_rgb_color(data.get('color'))
        )

    def clear(self):
        # This is really inefficent - Whats a better way?
        for i in range(len(self.dmx_universe)):
            self.dmx_universe[i] = 0