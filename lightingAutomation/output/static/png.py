import os
import logging
from multiprocessing import Process
from io import BytesIO

import PIL.Image

from ext.misc import hashfile, random_string
from ext.http_dispatch import http_dispatch

from lightingAutomation.render.sequence_manager import SequenceManager

log = logging.getLogger(__name__)

SALT = random_string()


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
        })

        # Exists
        sequence_filename = sequence_manager.get_filename(request_dict['path'].strip('/'))
        if not os.path.exists(sequence_filename):
            response_dict.update({'_status': '404 Not Found'})
            return response_dict

        # Etag
        sequence_hash = hashfile(sequence_filename)
        if request_dict.get('If-None-Match').strip() == (sequence_hash + SALT).strip():
            response_dict.update({'_status': '304 Not Modified'})
            return response_dict
        else:
            response_dict.update({
                'Etag': sequence_hash + SALT,
                'Cache-Control': f'max-age={60*60}',
            })

        if request_dict['method'] == 'GET':

            def render_png(sequence_filename):
                packer = sequence_manager.get_packer(sequence_filename)
                device_collection = sequence_manager.device_collection

                image = PIL.Image.new('RGB', (100, 100))
                image.putpixel((50, 50), (255, 0, 0))

                with BytesIO() as buffer:
                    image.save(buffer, 'PNG')
                    buffer.seek(0)
                    return buffer.read()

            # Render PNG to memory and set body of response
            response_dict.update({
                'Content-Type': 'image/png',
                '_body': render_png(sequence_filename),
            })

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