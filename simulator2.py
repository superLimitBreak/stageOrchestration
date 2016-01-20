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


# Device Renderers -------------------------------------------------------------

class DMXLightRGB(object):
    dmx_size = 3

    def __init__(self, address, x, y):
        self.address = address
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.dmx_size * 8, self.dmx_size * 5)
        self.func_get_data = lambda: []

    @property
    def data(self):
        return self.func_get_data()

    @property
    def color(self):
        return self.data

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class DMXLightRGBW(object):
    dmx_size = 4

    def __init__(self, address, x, y):
        self.address = address
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, self.dmx_size * 16, self.dmx_size * 10)
        self.func_get_data = lambda: []

    @property
    def data(self):
        return self.func_get_data()

    @property
    def color(self):
        red, green, blue, white = (c//2 for c in self.data[0:4])
        return (red + white, green + white, blue + white, 255)

    def render(self, screen):

        pygame.draw.rect(screen, self.color, self.rect)

        red, green, blue, white = self.data[0:4]
        def draw_led(value, color, y_offset):
            for i in range(value//32):
                pygame.draw.circle(screen, color, (self.dmx_size*2 + self.x + i * self.dmx_size*2, self.dmx_size*2 + self.y + y_offset * self.dmx_size*2), self.dmx_size*2//2)
        draw_led(red, (255, 0, 0), 0)
        draw_led(green, (0, 255, 0), 1)
        draw_led(blue, (0, 0, 255), 2)
        draw_led(white, (255, 255, 255), 3)


# Simulator --------------------------------------------------------------------

class DMXSimulator(ArtNet3, SimplePygameBase):

    def __init__(self, yamlpath, framerate=DEFAULT_FRAMERATE, **kwargs):
        ArtNet3.__init__(self)
        self.listen()

        SimplePygameBase.__init__(self, framerate=framerate)

        self.config = LightingConfig(yamlpath)

        self.state = tuple(random.randint(0, 255) for _ in range(512))  # Startup with a random DMX state

        self.dmx_items = []

        self.layout = open_yaml(os.path.join(yamlpath, 'simulator_layout.yaml'))
        for device_name, data in self.layout.items():
            x, y = data['x'], data['y']
            for index, device in enumerate(self.config.device_lookup[device_name]):
                
        exit()

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
