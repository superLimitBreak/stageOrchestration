import logging


log = logging.getLogger(__name__)


def render_sequence(packer, sequence_module, stage_description):
    """
    Render a lighting sequence to a binary intermediary
    """
    log.info(f'Rendering {name} {sequence_module}')
