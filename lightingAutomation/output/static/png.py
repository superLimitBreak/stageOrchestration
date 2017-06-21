import os
import logging
from multiprocessing import Process
from io import BytesIO

import PIL.Image

from ext.misc import hashfile, random_string, one_to_limit
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
    SALT = random_string() if options.get('postmortem') else ''  # Cachebust in development mode
    CACHE_CONTROL_SECONDS = 60 * 60

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
        sequence_hash = hashfile(sequence_filename) + SALT
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
                    options.get('framerate'),
                ),
            })

        return response_dict

    http_dispatch(func_dispatch)


def render_png(packer, device_collection, framerate=10, pixels_per_second=10):
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
