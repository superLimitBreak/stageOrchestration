import logging
from multiprocessing import Process

from ext.http_dispatch import http_dispatch

from lightingAutomation.render.sequence_manager import SequenceManager

log = logging.getLogger(__name__)


class StaticOutputPNG(object):
    def __init__(self, options):
        self.process = Process(target=serve_png, args=(options,))
        self.process.start()

    def close(self):
        self.process.join()


def serve_png(options):
    sequence_manager = SequenceManager(**options)

    def func_dispatch(request_dict, response_dict):
        response_dict.update({
            'Server': 'lightingAutomation/0.0.0 (Python3)',
            'Content-Type': 'image/png',
        })
        path = request_dict['path'].strip('/')

        try:
            packer = sequence_manager.get_packer(path)
        except AssertionError:
            response_dict.update({'_status': '404 Not Found'})
            return response_dict

        #if request_dict['method'] == 'GET':
        #    with open(filename, 'rb') as filehandle:
        #        response_dict['_body'] = filehandle.read()

        return response_dict

    http_dispatch(func_dispatch)


if __name__ == "__main__":
    serve_png({'required': 'test_options_are_missing'})

"""
    GET /sample.html HTTP/1.1
    Host: example.com
    If-Modified-Since: Wed, 01 Sep 2004 13:24:52 GMT
    If-None-Match: “4135cda4”

    HTTP/1.x 304 Not Modified
    Via: The-proxy-server
    Expires: Tue, 27 Dec 2005 11:25:19 GMT
    Date: Tue, 27 Dec 2005 05:25:19 GMT
    Server: Apache/1.3.33 (Unix) PHP/4.3.10
    Keep-Alive: timeout=2, max=99
    Etag: “4135cda4”
    Cache-Control: max-age=21600
"""