import logging

from .png import StaticOutputPNG


log = logging.getLogger(__name__)


class StaticOutputManager(object):
    def __init__(self, sequence_manager, settings):
        self.sequence_manager = sequence_manager
        self._output = {}

        # With settings init the required renderers
        if settings.get('http_png_port'):
            self._output['http_png_port'] = StaticOutputPNG(port=settings['http_png_port'])

    def close(self):
        for output in self._output.values():
            output.close()
