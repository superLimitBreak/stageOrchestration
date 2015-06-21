from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererLightTiming(AbstractDMXRenderer):
    def event(self, data):
        print('Netowork event: ', data)
