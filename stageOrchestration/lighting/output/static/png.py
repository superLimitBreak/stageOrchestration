import os
import logging
from multiprocessing import Process
from io import BytesIO
from collections import ChainMap
from itertools import chain

import PIL.Image

from ext.misc import hashfile, random_string, one_to_limit
from ext.http_dispatch import http_dispatch

from stageOrchestration.sequence_manager import SequenceManager

log = logging.getLogger(__name__)

DEFAULT_render_png_kwargs = {
    'framerate': 30,
    'pixels_per_second': 8,
    'frame_start': 0,
    'frame_end': None,
}


class StaticOutputPNG(object):
    def __init__(self, options):
        self.process = Process(target=serve_png, args=(options,))
        self.process.start()

    def close(self):
        self.process.join()


def serve_png(options, CACHE_CONTROL_SECONDS=60 * 60):
    sequence_manager = SequenceManager(**options)
    SALT = random_string() if options.get('postmortem') else ''  # Cachebust in development mode

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

        # Query String Parmas
        render_png_kwargs = {
            k: v
            for k, v in ChainMap(
                request_dict['query'],
                options,
                DEFAULT_render_png_kwargs,
            ).items()
            if k in DEFAULT_render_png_kwargs.keys()
        }

        # Etag
        sequence_hash = '|'.join(
            chain((hashfile(sequence_filename), SALT, request_dict['query'].get('cachebust', '')),
            map(str, render_png_kwargs.values()))
        )
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
                    **render_png_kwargs,
                ),
            })

        return response_dict

    http_dispatch(func_dispatch)


def render_png(packer, device_collection, framerate=None, pixels_per_second=DEFAULT_render_png_kwargs['pixels_per_second'], frame_start=0, frame_end=None):
    log.debug(f'render_png - framerate:{framerate} pixels_per_second:{pixels_per_second} frame_start:{frame_start} frame_end:{frame_end}')
    framerate = float(framerate)
    pixels_per_second = float(pixels_per_second)
    assert framerate > 0
    assert pixels_per_second
    frame_start = int(frame_start)
    frame_end = int(frame_end or packer.frames)
    assert frame_start >= 0
    assert frame_end > frame_start
    assert frame_end <= packer.frames

    image = PIL.Image.new('RGB', (frame_end - frame_start, len(device_collection.devices)))
    for frame_number in range(frame_start, frame_end):
        packer.restore_frame(frame_number)
        for device_number, device in enumerate(device_collection.get_devices()):
            image.putpixel((frame_number - frame_start, device_number), tuple(map(one_to_limit, device.rgb)))

    with BytesIO() as buffer:
        image.resize(
            # Resize image to have consistent pixels per second regardless of frame_rate of sequence
            (int((frame_end - frame_start) * (pixels_per_second / framerate)), image.height)
        ).save(buffer, 'PNG')
        return buffer.getvalue()


if __name__ == "__main__":
    serve_png({'required': 'test_options_are_missing'})
