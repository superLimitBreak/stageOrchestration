import os.path
import random

from libs.misc import postmortem
from libs.pygame_base import SimplePygameBase

from lighting.ArtNet3 import ArtNet3
from lighting import LightingConfig, open_yaml, add_default_argparse_args

import logging
log = logging.getLogger(__name__)


VERSION = '0.0.0'
DEFAULT_FRAMERATE = 15


class DMXSimulator(ArtNet3, SimplePygameBase):

    def __init__(self, yamlpath, framerate=DEFAULT_FRAMERATE, **kwargs):
        ArtNet3.__init__(self)
        self.listen()

        SimplePygameBase.__init__(self, framerate=framerate)

        self.config = LightingConfig(yamlpath)
        self.layout = open_yaml(os.path.join(yamlpath, 'simulator_layout.yaml'))

        self.state = tuple(random.randint(0, 255) for _ in range(512))  # Startup with a random DMX state

        self.dmx_items = []

    def loop(self):
        for item in self.dmx_items:
            item.render(self.screen)

    def update(self, state):
        self.state = state

    def recieve_dmx(self, data):
        self.update(data)


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""lightingAutomation simulator
        Listen to UDP DMX packets and visulise them
        """,
        epilog="""
        """
    )
    parser_input = parser

    parser.add_argument('-f', '--framerate', action='store', help='Frames per second to update the display. Should be in line with ArtNet rate', default=DEFAULT_FRAMERATE)

    add_default_argparse_args(parser, version=VERSION)

    args = parser.parse_args()
    return vars(args)


# Main -------------------------------------------------------------------------

if __name__ == "__main__":
    kwargs = get_args()
    logging.basicConfig(level=kwargs['log_level'])

    dmx = DMXSimulator(**kwargs)

    if kwargs.get('postmortem'):
        postmortem(dmx.start)
    else:
        dmx.start()
