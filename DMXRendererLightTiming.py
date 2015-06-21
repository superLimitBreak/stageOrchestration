from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererLightTiming(AbstractDMXRenderer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def network_event(self, data):
        print('DMXRendererLightTiming YEE HAW!', data)
