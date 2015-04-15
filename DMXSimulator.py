import pygame
import array

COLOR_BACKGROUND = (0, 0, 0, 255)


# Pygame Helpers ---------------------------------------------------------------
#  Try to keep underlying implementation/libs of grapics handling away from logic

class PygameBase(object):

    def __init__(self, framerate=3):
        pygame.init()
        self.screen = pygame.display.set_mode((320, 240))
        self.clock = pygame.time.Clock()
        self.running = True
        self.framerate = framerate
        self.start()

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

    def loop(self):
        assert False, 'loop must be overriden'


# DMX Simulator ----------------------------------------------------------------


class DXMLight(object):
    size = 8

    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        #self.func_get_data = func_get_data
        self.func_get_data = lambda: []

    @property
    def data(self):
        return self.func_get_data()

    @property
    def color(self):
        data = self.data
        return (data[0], data[1], data[2], 255)

    def render(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)


class DMXSimulator(PygameBase):

    def __init__(self):
        super().__init__()
        self._init_dmx_items(DMXLight(10, 10, 20), DMXLight(50, 50, 20), DMXLight(100, 100, 20))
        self.state = [0] * 512

    def _init_dmx_items(self, *dmx_items):
        self.dmx_items = dmx_items
        index = 0
        for dmx_item in dmx_items:
            dmx_item.func_get_data = lambda: self.state[index:index + dmx_item.size]
            index += dmx_item.size

    def loop(self):
        for item in self.dmx_items:
            item.render(self.screen)

    def update(self, state):
        self.state = state

if __name__ == "__main__":
    DMXSimulator()
