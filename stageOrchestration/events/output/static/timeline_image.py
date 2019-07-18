import os
import json
from io import BytesIO
import urllib.request
from collections import namedtuple

import PIL.Image

from calaldees.string_tools import substring_in

from stageOrchestration.http_image import HTTPImageRenderMixin
from stageOrchestration.events.model.triggerline import TriggerLine

import logging
log = logging.getLogger(__name__)


class HttpImageMediaTimelineRenderer(HTTPImageRenderMixin):

    DEFAULT_kwargs = {
        'pixels_per_second': 8,
        'image_format': 'png',
        'tracks': ('audio', 'front', 'rear', 'side'),
        'track_height': 64,
        'mediaTimelineImageExt': 'png',
    }

    def __init__(self, options):
        super().__init__(options)
        self.media_url = options['media_url']

    def get_etag(self, sequence_name):
        return self.sequence_manager.get_rendered_hash_media(sequence_name)

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

    _IMAGE_NONE = (0, 0, None)
    def trigger_to_image(trigger):
        assert isinstance(trigger, dict)
        if not trigger.get('src'):
            log.debug(f'no src for trigger. skipping')
            return _IMAGE_NONE

        # Load Image
        is_image_single = substring_in(('image',), (trigger.get('func', ''),))
        is_image_timeline = substring_in(('audio', 'video'), (trigger.get('func', ''),))
        assert is_image_single ^ is_image_timeline
        if is_image_single:
            url = os.path.join(media_url, trigger['src'])
        if is_image_timeline:
            url = f"{os.path.join(media_url, trigger['src'])}.{mediaTimelineImageExt}"
        try:
            media_image = PIL.Image.open(urllib.request.urlopen(url))
        except Exception:
            log.warning(f'unable to load image {url}')
            return _IMAGE_NONE
        if is_image_single:
            media_image = media_image.resize((
                int((media_image.height/media_image.width) * track_height),
                track_height,
            ))
        assert media_image.height == track_height

        if is_image_single:
            x1 = 0
            x2 = media_image.width
        if is_image_timeline:
            # ffmpeg with `--rate` seems to continuiously sample 1 second behind the expect.
            # This constant is BAD. My options were.
            # Have the first frame positioned and timed correctly OR
            # Have all other frames correct and the slightly crop the first frame.
            FFMPEG_CORRECT_CONSTANT = int(pixels_per_second)
            x1 = int(min(
                media_image.width,
                trigger['position'] * pixels_per_second
            )) + FFMPEG_CORRECT_CONSTANT
            x2 = int(max(
                x1,
                (trigger['duration'] - trigger['position']) * pixels_per_second
            ))
        media_image = media_image.crop((
            x1, 0,
            x2, media_image.height,
        ))
        return (
            tracks.index(trigger['deviceid']),
            int(trigger['timestamp'] * pixels_per_second),
            media_image
        )

    trigger_media_list = tuple(map(trigger_to_image, triggerline.triggers))
    width = max((x+img.width for _, x, img in trigger_media_list if img))
    image = PIL.Image.new('RGB', (width, len(tracks) * track_height))

    for (row, x, img) in trigger_media_list:
        if img:
            image.paste(img, (x, row * track_height))

    with BytesIO() as buffer:
        image.save(buffer, image_format)
        return buffer.getvalue()
