import array


class AbstractDMXRenderer(object):
    DEFAULT_DMX_SIZE = 128

    def __init__(self, dmx_size=DEFAULT_DMX_SIZE):
        self.dmx_universe = array.array('B')
        self.dmx_universe.frombytes(b'\xff'*dmx_size)

    def render(self, frame):
        """
        Given a frame number (that can be ignored)
        Return a dmx_universe byte array
        """
        #raise Exception('should override')
        return self.dmx_universe

    def close(self):
        #raise Exception('should override')
        pass

    def event(self, data):
        #raise Exception('should override')
        pass


def mix(destination, *sources):
    for index, values in enumerate(zip(*sources)):
        destination[index] = max(values)
