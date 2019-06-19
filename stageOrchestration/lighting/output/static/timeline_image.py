import os
from io import BytesIO
from itertools import chain

import falcon
import PIL.Image

from calaldees.string_tools import random_string
from calaldees.limit import one_to_limit

from stageOrchestration.sequence_manager import SequenceManager

import logging
log = logging.getLogger(__name__)


class HttpLightTimelineRenderer():

    DEFAULT_render_png_kwargs = {
        'framerate': 30,
        'pixels_per_second': 8,
        'frame_start': 0,
        'frame_end': None,
        'image_format': 'png',
    }

    def __init__(self, options):
        self.sequence_manager = SequenceManager(**options)
        self.options = options
        self.instance_id = random_string() if options.get('postmortem') else ''

    def on_get(self, request, response, sequence_name=None):
        #import pdb ; pdb.set_trace()
        # Exists
        sequence_filename = self.sequence_manager.get_rendered_filename(sequence_name)
        if not os.path.isfile(sequence_filename):
            response.media = {'error': 'file not found'}
            response.status = falcon.HTTP_400
            return

        # Args
        render_png_kwargs = {
            k: v
            for k, v in {
                **self.DEFAULT_render_png_kwargs,
                **self.options,
                **request.params,
            }.items()
            if k in self.DEFAULT_render_png_kwargs.keys()
        }

        # ETag
        content_etag = '|'.join(chain(
            (
                self.instance_id,
                request.params.get('cachebust') or self.sequence_manager.get_rendered_hash(sequence_filename),
            ),
            map(str, render_png_kwargs.values()),
        ))
        if content_etag in (request.if_none_match or ''):
            response.status = falcon.HTTP_304
            return
        response.etag = content_etag

        # Render
        response.content_type = 'image/png'
        try:
            response.body = render_light_timeline_image(
                self.sequence_manager.get_packer(sequence_filename),
                self.sequence_manager.device_collection,
                **render_png_kwargs,
            )
        except Exception as ex:
            #response.media = {'error': 'unable to extract metadata', 'reason': str(ex)}
            response.status = falcon.HTTP_500
            return
        response.status = falcon.HTTP_200


def render_light_timeline_image(
        packer,
        device_collection,
        framerate=None,
        pixels_per_second=HttpLightTimelineRenderer.DEFAULT_render_png_kwargs['pixels_per_second'],
        frame_start=0,
        frame_end=None,
        image_format='png',
):
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
        ).save(buffer, image_format)
        return buffer.getvalue()
