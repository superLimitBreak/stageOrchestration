import os
import json
from io import BytesIO
import urllib.request
from collections import namedtuple

import PIL.Image

from stageOrchestration.http_image import HTTPImageRenderMixin
from stageOrchestration.events.model.triggerline import TriggerLine

import logging
log = logging.getLogger(__name__)


class HttpImageMediaTimelineRenderer(HTTPImageRenderMixin):

    DEFAULT_kwargs = {
        'pixels_per_second': 8,
        'image_format': 'png',
        'tracks': ('audio', 'front', 'rear'),
        'track_height': 64,
        'mediaTimelineImageExt': 'png',
    }

    def __init__(self, options):
        super().__init__(options)
        self.media_url = options['media_url']

    def render(self, sequence_name=None, **kwargs):
        assert sequence_name, 'sequence_name not provided'
        with open(self.sequence_manager.get_rendered_trigger_filename(sequence_name), 'rt') as filehandle:
            triggerline = TriggerLine(json.load(filehandle))

        return render_media_timeline_image(triggerline, media_url=self.media_url, **kwargs)


TimelineImage = namedtuple('TimelineImage', ('row', 'x', 'image'))


def render_media_timeline_image(
        triggerline,
        media_url='',
        pixels_per_second=HttpImageMediaTimelineRenderer.DEFAULT_kwargs['pixels_per_second'],
        image_format=HttpImageMediaTimelineRenderer.DEFAULT_kwargs['image_format'],
        tracks=HttpImageMediaTimelineRenderer.DEFAULT_kwargs['tracks'],
        track_height=HttpImageMediaTimelineRenderer.DEFAULT_kwargs['track_height'],
        mediaTimelineImageExt=HttpImageMediaTimelineRenderer.DEFAULT_kwargs['mediaTimelineImageExt'],
):
    assert media_url
    if isinstance(tracks, str):
        tracks = tuple(track.strip() for track in tracks.split(','))
    pixels_per_second = float(pixels_per_second)
    assert pixels_per_second
    track_height = int(track_height)
    assert track_height > 0


    def trigger_to_image(trigger):
        media_src = trigger['src']
        url = f'{os.path.join(media_url, media_src)}.{mediaTimelineImageExt}'
        try:
            media_image = PIL.Image.open(urllib.request.urlopen(url))
        except Exception:
            log.warn(f'unable to load image {url}')
            return (0, 0, None)

        media_image = media_image.crop((
            int(min(
                media_image.width,
                trigger['position'] * pixels_per_second
            )), 0,
            int(max(
                media_image.width,
                (trigger['duration'] - trigger['position']) * pixels_per_second
            )), media_image.height
        ))
        return (
            tracks.index(trigger['deviceid']),
            int(trigger['timestamp'] * pixels_per_second),
            media_image
        )

    trigger_media_list = tuple(map(trigger_to_image, triggerline.triggers))
    width = int(max((x+img.width for _, x, img in trigger_media_list if img)))
    image = PIL.Image.new('RGB', (width, len(tracks) * track_height))

    for (row, x, img) in trigger_media_list:
        if img:
            image.paste(img, (x, row * track_height))

    with BytesIO() as buffer:
        image.save(buffer, image_format)
        return buffer.getvalue()
