from multiprocessing import Process

import falcon

from stageOrchestration.lighting.output.static.timeline_image import HttpImageLightTimelineRenderer
from stageOrchestration.events.output.static.timeline_image import HttpImageMediaTimelineRenderer

import logging
log = logging.getLogger(__name__)


class HTTPServer(object):
    def __init__(self, options):
        self.process = Process(target=serve_process, args=(options,))
        self.process.start()
        #serve_process(options)

    def close(self):
        self.process.join()


def serve_process(options):
    from wsgiref import simple_server
    httpd = simple_server.make_server('0.0.0.0', options.get('http_png_port'), create_wsgi_app(options))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


def create_wsgi_app(options):
    app = falcon.API()
    app.add_route('/lights/{sequence_name}', HttpImageLightTimelineRenderer(options))
    app.add_route('/media/{sequence_name}', HttpImageMediaTimelineRenderer(options))
    return app
