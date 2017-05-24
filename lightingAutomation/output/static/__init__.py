import logging

from .png import StaticOutputPNG


log = logging.getLogger(__name__)


class StaticOutputManager(object):
    def __init__(self, options):
        self._output = {}

        # With settings init the required renderers
        if options.get('http_png_port'):
            self._output['http_png_port'] = StaticOutputPNG(options)

    def close(self):
        for output in self._output.values():
            output.close()
