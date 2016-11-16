import logging


log = logging.getLogger(__name__)


def render_sequence(packer, sequence_module, device_collection):
    """
    Render a lighting sequence to a binary intermediary
    """
    log.debug(f'Rendering {sequence_module._sequence_name}')
    packer.save_frame()
