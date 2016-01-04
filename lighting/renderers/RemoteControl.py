from lighting import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class RemoteControl(AbstractDMXRenderer):
    """
    Using the lighting config data, control the dmx lights from a remote source
    using json display trigger events
    """
    __name__ = 'lights'

    def __init__(self, lighting_config):
        super().__init__()
        self.config = lighting_config

    def set(self, data):
        log.info('set')
