import random

from libs.pygame_base import SimplePygameBase
from lighting.ArtNet3 import ArtNet3


class DMXSimulator(ArtNet3, SimplePygameBase):

    def __init__(self, framerate=15):
        ArtNet3.__init__(self)
        self.listen()

        SimplePygameBase.__init__(self, framerate=framerate)

        self.state = tuple(random.randint(0, 255) for _ in range(512))  # Startup with a random DMX state

        self.dmx_items = []

    def loop(self):
        for item in self.dmx_items:
            item.render(self.screen)

    def update(self, state):
        self.state = state

    def recieve_dmx(self, data):
        self.update(data)


# Main -------------------------------------------------------------------------

if __name__ == "__main__":
    dmx = DMXSimulator()
    dmx.start()
