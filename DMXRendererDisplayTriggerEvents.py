"""
Plugin for responding to other network events to stop the lighting system
"""

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererDisplayTriggerEvents(AbstractDMXRenderer):

    __name__ = 'trigger'

    def __init__(self, dmx_lighting_renderer):
        super().__init__()
        self.dmx_lighting_renderer = dmx_lighting_renderer

    def empty(self, data):
        print('empty', data)

    def stop(self, data):
        print('stop', data)
