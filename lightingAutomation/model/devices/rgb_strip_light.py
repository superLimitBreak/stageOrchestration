from ext.attribute_packer import CollectionPackerMixin
from .rgb_light import RGBLight


class RGBStripLight(CollectionPackerMixin):
    def __init__(self, size, red=0, green=0, blue=0):
        self.lights = tuple(RGBLight(red=red, green=green, blue=blue) for i in range(size))
        CollectionPackerMixin.__init__(self, self.lights)

    def _average_group_attr(self, attr):
        return sum(getattr(light, attr) for light in self.lights) / len(self.lights)
    def _set_group_attr(self, attr, value):
        for light in self.lights:
            setattr(light, attr, value)

    @property
    def red(self):
        return self._average_attr('red')
    @red.setter
    def red(self, value):
        self._set_group_attr('red', value)

    @property
    def green(self):
        return self._average_attr('green')
    @green.setter
    def green(self, value):
        self._set_group_attr('green', value)

    @property
    def blue(self):
        return self._average_attr('blue')
    @blue.setter
    def blue(self, value):
        self._set_group_attr('blue', value)

    @property
    def rgb(self):
        return (self.red, self.green, self.blue)
    @rgb.setter
    def rgb(self, rgb):
        self.red, self.green, self.blue = rgb

    def reset(self):
        for light in self.lights:
            light.reset()

    def todict(self):
        return tuple(light.todict() for light in self.lights)
