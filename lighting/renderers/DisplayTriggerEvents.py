from lighting import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DisplayTriggerEvents(AbstractDMXRenderer):
    """
    Plugin for responding to other network events to stop the lighting system
    """
    __name__ = 'trigger'

    def __init__(self, renderers):
        super().__init__()
        self.renderers = tuple(renderers)

    def empty(self, data):
        log.info('empty')
        self.clear(data)

    def stop(self, data):
        log.info('stop')
        self.clear(data)

    def clear(self, data):
        for renderer in self.renderers:
            for method in ('clear', 'stop', 'empty'):
                getattr(renderer, method, lambda: None)()
