import logging

from ext.timeline import Timeline

log = logging.getLogger(__name__)

RENDER_FUNCTION = 'get_timeline'


def render_binary_sequence(packer, sequence_module, device_collection, frame_rate=30):
    """
    Render a lighting sequence to a binary intermediary
    """
    timeline = getattr(sequence_module, RENDER_FUNCTION)(device_collection)
    assert isinstance(timeline, Timeline)
    renderer = timeline.get_renderer()

    log.debug(f'Rendering {sequence_module._sequence_name}')
    for timecode in (0,):
        renderer.render(timecode)
        packer.save_frame()
