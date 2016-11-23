import logging

from ext.timeline import Timeline

log = logging.getLogger(__name__)

TIMELINE_ATTRIBUTE_NAME = 'TIMELINE'

def render_binary_sequence(packer, sequence_module, device_collection):
    """
    Render a lighting sequence to a binary intermediary
    """
    assert isinstance(getattr(sequence_module, TIMELINE_ATTRIBUTE_NAME), Timeline), \
        f'{sequence_module.__name__} does not have required {TIMELINE_ATTRIBUTE_NAME}'

    log.debug(f'Rendering {sequence_module._sequence_name}')
    packer.save_frame()
