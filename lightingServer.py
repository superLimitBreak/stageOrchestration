import logging

import yaml

from ext.misc import postmortem

from __init__ import VERSION

log = logging.getLogger(__name__)


# Constants --------------------------------------------------------------------

DESCRIPTION = """
    lightingAutomation - Stage Orchestration Framework
"""

DEFAULT_CONFIG_FILENAME = 'config.yaml'


# Command Line Arguments -------------------------------------------------------

def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description=DESCRIPTION,
    )

    parser.add_argument('--config', action='store', help='', default=DEFAULT_CONFIG_FILENAME)
    parser.add_argument('--displaytrigger_host', action='store', help='display-trigger server to recieve events from')
    parser.add_argument('--framerate', action='store', help='Frames per second', type=float)
    parser.add_argument('--artnet_dmx_host', action='store', help='ArtNet3 ip address')
    parser.add_argument('--scaninterval', action='store', type=float, help='seconds to scan datafiles for changes')

    parser.add_argument('--postmortem', action='store_true', help='Enter debugger on exception')
    parser.add_argument('--log_level', type=int, help='log level', default=logging.INFO)

    parser.add_argument('--version', action='version', version=VERSION)

    kwargs = vars(parser.parse_args())

    # Overlay config defaults from file
    with open(kwargs['config'], 'rt') as config_filehandle:
        config = yaml.load(config_filehandle)
        kwargs = {k: v if v is not None else config.get(k) for k, v in kwargs.items()}

    return kwargs


# Main -------------------------------------------------------------------------

def main(**kwargs):
    log.info('lightingAutomation')


if __name__ == "__main__":
    kwargs = get_args()
    logging.basicConfig(level=kwargs['log_level'])

    def launch():
        main(**kwargs)
    if kwargs.get('postmortem'):
        postmortem(launch)
    else:
        launch()
