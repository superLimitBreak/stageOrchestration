import array


class AbstractDMXRenderer(object):
    DEFAULT_DMX_SIZE = 128

    @staticmethod
    def new_dmx_array(dmx_size=DEFAULT_DMX_SIZE):
        dmx_universe = array.array('B')
        return dmx_universe.frombytes(b'\xff'*dmx_size)

    def __init__(self, dmx_size=DEFAULT_DMX_SIZE):
        self.dmx_universe = self.new_dmx_array(dmx_size)

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


def mix(destination, sources, mix_func=max):
    for index, values in enumerate(zip(*sources)):
        destination[index] = mix_func(values)


def get_value_at(sequence, target, get_value_item_func):
    current = 0
    for index, item in enumerate(sequence):
        item_value = get_value_item_func(item)
        if target >= current and target < current + item_value:
            return item, target - current, index
        current += item_value
    return None, target - current, None
