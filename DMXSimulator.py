import array
import random


# Pygame Helpers ---------------------------------------------------------------
#  Try to keep underlying implementation/libs of grapics handling away from logic

import pygame

COLOR_BACKGROUND = (0, 0, 0, 255)


class PygameBase(object):

    def __init__(self, framerate=3):
        pygame.init()
        self.screen = pygame.display.set_mode((320, 240))
        self.clock = pygame.time.Clock()
        self.running = True
        self.framerate = framerate

    def start(self):
        while self.running:
            self.clock.tick(self.framerate)
            self.screen.fill(COLOR_BACKGROUND)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.running = False

            self.loop()

            pygame.display.flip()

        pygame.quit()

    def stop(self):
        self.running = False

    def loop(self):
        assert False, 'loop must be overriden'


# DMXUDPMixin ------------------------------------------------------------------

from libs.udp import UDPMixin

class DMXUDPMixin(UDPMixin):
    """
    Passthrough to make UDPMixin behave like the ArtNet3 Mixin
    This allows simple testing of just displaying a binary dmx string to the lights
    without the need of real artnet packet complexity
    """
    def _recieve(self, addr, data):
        self.recieve_dmx(data)

def _send_example():
    """
    DMXUDPMixin send example
    Use these in a terminal for testing
    """
    import socket ; sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(b'HelloWorld', ('127.0.0.1', 5005))
    sock.sendto(b'\x00'*512, ('127.0.0.1', 5005))
    sock.sendto(b'Art-Net\x00P\x00\x00\x0e\x00\x00\x00\x00\x00\x04\x00\x01\x02\x03', ('127.0.0.1', 0x1936))


# DMX Simulator ----------------------------------------------------------------

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


from ArtNet3 import ArtNet3


class DMXSimulator(ArtNet3, PygameBase):

    def __init__(self, framerate=30):
        ArtNet3.__init__(self)
        self.listen()

        PygameBase.__init__(self, framerate=framerate)

        self._init_dmx_items(
            DMXLightRGBW(0, 0, 140),
            DMXLightRGBW(8, 0, 100),
            DMXLightRGBW(16, 0, 0),
            DMXLightRGBW(24, 64, 0),
            DMXLightRGBW(32, 128, 0),
            DMXLightRGBW(40, 184, 0),
            DMXLightRGBW(48, 256, 0),
            DMXLightRGBW(56, 284, 100),

            DMXLightRGB(66, 0, 200),
            DMXLightRGB(69, 0+24, 200),
            DMXLightRGB(72, 0+48, 200),

            DMXLightRGB(77, 96, 200),
            DMXLightRGB(80, 96+24, 200),
            DMXLightRGB(83, 96+48, 200),

            DMXLightRGB(88, 192, 200),
            DMXLightRGB(91, 192+24, 200),
            DMXLightRGB(94, 192+48, 200),

            DMXLightRGB(88, 288, 200),
            DMXLightRGB(91, 288+24, 200),
            DMXLightRGB(94, 288+48, 200),

        )
        self.state = [random.randint(0, 255) for i in range(512)]  # Startup with a completlty random DMX state

    def _init_dmx_items(self, *dmx_items):
        self.dmx_items = dmx_items
        for dmx_item in dmx_items:
            def func_get_data(index, size):
                return lambda: self.state[index:index + size]
            dmx_item.func_get_data = func_get_data(dmx_item.address, dmx_item.dmx_size)

    def loop(self):
        for item in self.dmx_items:
            item.render(self.screen)

    def update(self, state):
        self.state = state

    def recieve_dmx(self, data):
        #if (hasattr(self, 'state') and data != self.state):
        #    print(data)
        self.update(data)


# Main -------------------------------------------------------------------------

if __name__ == "__main__":
    dmx = DMXSimulator()
    dmx.start()
