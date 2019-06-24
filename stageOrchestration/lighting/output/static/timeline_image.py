from io import BytesIO

import PIL.Image

from calaldees.limit import one_to_limit

from stageOrchestration.http_image import HTTPImageRenderMixin

import logging
log = logging.getLogger(__name__)


class HttpImageLightTimelineRenderer(HTTPImageRenderMixin):

    DEFAULT_kwargs = {
        'framerate': 30,
        'pixels_per_second': 8,
        'frame_start': 0,
        'frame_end': None,
        'image_format': 'png',
    }

    def get_etag(self, sequence_name):
        return self.sequence_manager.get_rendered_hash_lights(sequence_name)

    def render(self, sequence_name=None, **kwargs):
        assert sequence_name
        return render_light_timeline_image(
            self.sequence_manager.get_packer(sequence_name),
            self.sequence_manager.device_collection,
            **kwargs,
        )


def render_light_timeline_image(
        packer,
        device_collection,
        framerate=None,
        pixels_per_second=HttpImageLightTimelineRenderer.DEFAULT_kwargs['pixels_per_second'],
        frame_start=0,
        frame_end=None,
        image_format=HttpImageLightTimelineRenderer.DEFAULT_kwargs['image_format'],
):
    log.debug(f'render_light_timeline_image - framerate:{framerate} pixels_per_second:{pixels_per_second} frame_start:{frame_start} frame_end:{frame_end}')

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
