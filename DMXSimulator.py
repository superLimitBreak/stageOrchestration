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

class DMXSimulator(PygameBase):

    def __init__(self):
        super().__init__()
        self.state = array.array('B')

    def loop(self):
        pass

    def update(self, state):
        self.state = state

if __name__ == "__main__":
    DMXSimulator()
