from copy import copy
from functools import partial
import logging

from ext.music import get_time, parse_timesigniture

log = logging.getLogger(__name__)

RENDER_FUNCTION = 'create_timeline'
META_ATTRIBUTE = 'META'
DEFAULT_META = {
    'name': 'Unknown',
    'bpm': 120,
    'timesigniture': '4:4',
}

def render_binary_sequence(packer, sequence_module, device_collection, frame_rate=30, default_meta=DEFAULT_META):
    """
    Render a lighting sequence to a binary intermediary
    packer is managing/monitoring device_collection -> packer.save saves the frames state
    """

    meta = copy(default_meta)
    meta.update(getattr(sequence_module, META_ATTRIBUTE, {}))
    get_time_func = partial(get_time, timesigniture=parse_timesigniture(meta['timesigniture']), bpm=meta['bpm'])

    timeline = getattr(sequence_module, RENDER_FUNCTION)(device_collection, get_time_func)
    assert timeline, f'{sequence_module.__name__} did not return a timeline'
    assert timeline.duration, f'{sequence_module.__name__} timeline does not contain any items to animate'

    log.debug(f'Rendering {sequence_module._sequence_name}')
    renderer = timeline.get_renderer()
    frames = int(timeline.duration * frame_rate)
    for timecode in ((frame/frames)*timeline.duration for frame in range(frames)):
        renderer.render(timecode)
        packer.save_frame()
