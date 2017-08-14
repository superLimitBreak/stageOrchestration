import os
import logging
from multiprocessing import Process
from io import BytesIO

import PIL.Image

from ext.misc import hashfile, random_string, one_to_limit
from ext.http_dispatch import http_dispatch

from stageOrchestration.sequence_manager import SequenceManager

log = logging.getLogger(__name__)

DEFAULT_PIXELS_PER_SECOND = 8
DEFAULT_FRAMERATE = 30


class StaticOutputPNG(object):
    def __init__(self, options):
        self.process = Process(target=serve_png, args=(options,))
        self.process.start()

    def close(self):
        self.process.join()


def serve_png(options):
    sequence_manager = SequenceManager(**options)
    SALT = random_string() if options.get('postmortem') else ''  # Cachebust in development mode
    CACHE_CONTROL_SECONDS = 60 * 60

    def func_dispatch(request_dict, response_dict):
        request_dict['query'] = {k: ', '.join(v) for k, v in request_dict['query'].items()}  # Flatten querystring
        response_dict.update({
            'Server': 'stageOrchestration/0.0.0 (Python3)',
        })

        # Exists
        sequence_filename = sequence_manager.get_rendered_filename(request_dict['path'].strip('/'))
        if not os.path.exists(sequence_filename):
            response_dict.update({'_status': '404 Not Found'})
            return response_dict

        def hash_query_fields(*fields):
            return '|'.join(request_dict['query'].get(field, '') for field in fields)

        # Etag
        sequence_hash = hashfile(sequence_filename) + hash_query_fields('framerate', 'pixels_per_second') + SALT
        if sequence_hash in request_dict.get('If-None-Match', ''):
            response_dict.update({'_status': '304 Not Modified'})
            return response_dict
        else:
            response_dict.update({'Etag': f'\W {sequence_hash}', 'Cache-Control': f'max-age={CACHE_CONTROL_SECONDS}'})

        # Render body
        if request_dict['method'] == 'GET':
            response_dict.update({
                'Content-Type': 'image/png',
                '_body': render_png(
                    sequence_manager.get_packer(sequence_filename),
                    sequence_manager.device_collection,
                    framerate=request_dict['query'].get('framerate', options.get('framerate', DEFAULT_FRAMERATE)),
                    pixels_per_second=request_dict['query'].get('pixels_per_second', options.get('http_png_pixels_per_second', DEFAULT_PIXELS_PER_SECOND))
                ),
            })

        return response_dict

    http_dispatch(func_dispatch)


def render_png(packer, device_collection, framerate=None, pixels_per_second=DEFAULT_PIXELS_PER_SECOND):
    log.info(f'framerate: {framerate} pixels_per_second:{pixels_per_second}')
    framerate = float(framerate)
    pixels_per_second = float(pixels_per_second)
    assert framerate > 0
    assert pixels_per_second
    image = PIL.Image.new('RGB', (packer.frames, len(device_collection.devices)))
    for frame_number in range(packer.frames):
        packer.restore_frame(frame_number)
        for device_number, device in enumerate(device_collection.get_devices()):
            image.putpixel((frame_number, device_number), tuple(map(one_to_limit, device.rgb)))

    with BytesIO() as buffer:
        image.resize(
            # Resize image to have consistent pixels per second regardless of frame_rate of sequence
            (int(packer.frames * (pixels_per_second / framerate)), image.height)
        ).save(buffer, 'PNG')
        return buffer.getvalue()


if __name__ == "__main__":
    serve_png({'required': 'test_options_are_missing'})
