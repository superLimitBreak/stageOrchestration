import logging


log = logging.getLogger(__name__)


def render_sequence(name, sequence_module):
    """
    Render a lighting sequence to a binary intermediary
    """
    log.info(f'Rendering {name} {sequence_module}')
