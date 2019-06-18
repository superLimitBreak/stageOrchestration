from multiprocessing import Process

from calaldees.string_tools import random_string
from calaldees.net.http_dispatch import http_dispatch

from stageOrchestration.lighting.output.static.png import get_serve_light_png_function

import logging
log = logging.getLogger(__name__)


# Ok ... so let me level with you
#  I'm sorry ...
#  http dispatch is a complex problem
#  I wrote http_dispatch and this thread as a learning exercise
#  It has grown beyond a simple experiment.
#  This can probably be replaced with simple_http or another simple framework. falcon?


class HTTPServer(object):
    def __init__(self, options):
        self.process = Process(target=serve_process, args=(options,))
        self.process.start()

    def close(self):
        self.process.join()


def serve_process(options, CACHE_CONTROL_SECONDS=60 * 60):
    request_dict_overlay = {
        # SALT - Cachebust for instance of development code
        #   When we restart the python code - we need a new ID
        'SALT': random_string() if options.get('postmortem') else '',
        'CACHE_CONTROL_SECONDS': CACHE_CONTROL_SECONDS,
    }

    routes = {
        'lights': get_serve_light_png_function(options),
        #'media': get_serve_media_timeline_png_function(options),
    }

    def func_dispatch(request_dict, response_dict):
        request_dict.update(request_dict_overlay)
        request_dict['query'] = {k: ', '.join(v) for k, v in request_dict['query'].items()}  # Flatten querystring
        response_dict.update({
            'Server': 'stageOrchestration/0.0.0 (Python3)',
        })
        path_segments = request_dict['path'].split('/')
        if path_segments[0] not in routes:
            response_dict.update({'_status': '404 Not Found'})
            return response_dict
        request_dict['path'] = '/'.join(path_segments[1:])
        return routes[path_segments[0]](request_dict, response_dict)

    http_dispatch(func_dispatch, port=options.get('http_png_port'))
