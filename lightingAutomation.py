import logging

import yaml

from ext.misc import postmortem

from __init__ import VERSION

log = logging.getLogger(__name__)


# Constants --------------------------------------------------------------------

DESCRIPTION = """
    lightingAutomation - Stage Orchistration Framework
"""

DEFAULT_CONFIG_FILENAME = 'config.yaml'


# Command Line Arguments -------------------------------------------------------

def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description=DESCRIPTION,
    )

    # Core
    parser.add_argument('--config', action='store', help='', default=DEFAULT_CONFIG_FILENAME)
    parser.add_argument('--displaytrigger_host', action='store', help='display-trigger server to recieve events from')
    parser.add_argument('-f', '--framerate', action='store', help='Frames per second', type=int)
    parser.add_argument('--artnet_dmx_host', action='store', help='ArtNet3 ip address')

    # Plugin params
    parser.add_argument('--yamlscaninterval', action='store', type=float, help='seconds to scan')

    parser.add_argument('--postmortem', action='store_true', help='Enter debugger on exception')
    parser.add_argument('--log_level', type=int, help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=VERSION)

    kwargs = vars(parser.parse_args())

    # Overlay config defaults from file
    with open(kwargs['config'], 'rt') as config_filehandle:
        config = yaml.load(config_filehandle)
        kwargs = {k: v or config.get(k) for k, v in kwargs.items()}

    return kwargs


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
