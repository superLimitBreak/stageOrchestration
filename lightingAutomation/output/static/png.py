from ext.http_dispatch import http_dispatch

import logging
log = logging.getLogger(__name__)


class StaticOutputPNG(object):
    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass

    def serve(self):
        http_dispatch(self.func_dispatch)

    def func_dispatch(self, request_dict, response_dict):
        log.info(request_dict)

        filename = '/Users/allan.callaghan/temp/test.png'

        response_dict.update({
            'Server': 'lightingAutomation/0.0.0 (Python3)',
            'Content-Type': 'image/png',
            #'Content-Length': os.stat(filename).st_size,
        })

        if request_dict['method'] == 'GET':
            with open(filename, 'rb') as filehandle:
                response_dict['_body'] = filehandle.read()

        return response_dict

if __name__ == "__main__":
    ss = StaticOutputPNG()
    http_dispatch(ss.func_dispatch)

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