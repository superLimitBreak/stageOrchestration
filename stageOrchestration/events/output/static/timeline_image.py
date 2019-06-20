import os
import json
from io import BytesIO
import urllib.request

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
    }

    def __init__(self, options):
        super().__init__(options)
        self.media_url = options['media_url']

    def render(self, sequence_filename=None, **kwargs):
        assert sequence_filename
        with open(self.sequence_manager.get_rendered_trigger_filename(sequence_filename), 'rt') as filehandle:
            triggerline = TriggerLine(json.load(filehandle))

        return render_media_timeline_image(triggerline, media_url=self.media_url, **kwargs)


def render_media_timeline_image(
        triggerline,
        media_url='',
        pixels_per_second=HttpImageMediaTimelineRenderer.DEFAULT_kwargs['pixels_per_second'],
        image_format=HttpImageMediaTimelineRenderer.DEFAULT_kwargs['image_format'],
        tracks=HttpImageMediaTimelineRenderer.DEFAULT_kwargs['tracks'],
        track_height=HttpImageMediaTimelineRenderer.DEFAULT_kwargs['track_height'],
):
    log.debug(f'')

    assert media_url
    if isinstance(tracks, str):
        tracks = tuple(track.strip() for track in tracks.split(','))
    pixels_per_second = float(pixels_per_second)
    assert pixels_per_second
    track_height = int(track_height)
    assert track_height > 0

    #media_image = Image.open(urllib.request.urlopen(os.path.join(media_url, media_filename)))

    # 'json_state_continuous': self.triggerline.get_triggers_at,
    # 'json_single_triggers': self.triggerline_renderer.get_triggers_at,

    width = 64

    image = PIL.Image.new('RGB', (width, len(tracks) * track_height))

    with BytesIO() as buffer:
        image.save(buffer, image_format)
        return buffer.getvalue()
