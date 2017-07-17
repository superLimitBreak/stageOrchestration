import logging

log = logging.getLogger(__name__)

RENDER_FUNCTION = 'create_timeline'


def render_binary_sequence(packer, sequence_module, device_collection, get_time_func, frame_rate=30):
    """
    Render a lighting sequence to a binary intermediary
    packer is managing/monitoring device_collection -> packer.save saves the frames state
    """
    device_collection.reset()

    timeline = getattr(sequence_module, RENDER_FUNCTION)(device_collection, get_time_func)
    assert timeline, f'{sequence_module.__name__} did not return a timeline'
    assert timeline.duration, f'{sequence_module.__name__} timeline does not contain any items to animate'

    log.debug(f'Rendering {sequence_module._sequence_name}')
    renderer = timeline.get_renderer()
    frames = int(timeline.duration * frame_rate)
    for timecode in ((frame/frames)*timeline.duration for frame in range(frames+1)):
        renderer.render(timecode)
        packer.save_frame()
