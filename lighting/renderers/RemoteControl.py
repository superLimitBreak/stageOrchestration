from lighting import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class RemoteControl(AbstractDMXRenderer):
    __name__ = 'lights'

    def __init__(self):
        super().__init__()

    def set(self, data):
        log.info('set state')
