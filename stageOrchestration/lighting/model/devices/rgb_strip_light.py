from copy import copy

from ext.attribute_packer import CollectionPackerMixin
from .rgb_light import RGBLight


class RGBStripLight(CollectionPackerMixin):
    def __init__(self, size=0, red=0, green=0, blue=0, lights=()):
        assert bool(size) ^ bool(lights), 'Either provide a size or a template of lights to copy'
        if lights:
            self.lights = tuple(copy(light) for light in lights)
        else:
            self.lights = tuple(RGBLight(red=red, green=green, blue=blue) for i in range(size))
        CollectionPackerMixin.__init__(self, self.lights)

    def __copy__(self):
        return RGBStripLight(lights=self.lights)

    def _average_group_attr(self, attr):
        return sum(getattr(light, attr) for light in self.lights) / len(self.lights)
    def _set_group_attr(self, attr, value):
        for light in self.lights:
            setattr(light, attr, value)

    @property
    def red(self):
        return self._average_group_attr('red')
    @red.setter
    def red(self, value):
        self._set_group_attr('red', value)

    @property
    def green(self):
        return self._average_group_attr('green')
    @green.setter
    def green(self, value):
        self._set_group_attr('green', value)

    @property
    def blue(self):
        return self._average_group_attr('blue')
    @blue.setter
    def blue(self, value):
        self._set_group_attr('blue', value)

    @property
    def rgb(self):
        return (self.red, self.green, self.blue)
    @rgb.setter
    def rgb(self, rgb):
        self.red, self.green, self.blue = rgb

    # BaseDevice Ducktyping -------------

    def reset(self):
        for light in self.lights:
            light.reset()

    def todict(self):
        return tuple(light.todict() for light in self.lights)

    def _and_(lights1, lights2):
        for lights in (lights1, lights2):
            assert isinstance(lights, RGBStripLight)
        assert len(lights1.lights) == len(lights2.lights), 'Strip lights can only be merged if they are the same size'
        for index, light1 in enumerate(lights1.lights):
            light1._and_(lights2.lights[index])

    def __and__(lights1, lights2):
        t = copy(lights1)
        t._and_(lights2)
        return t

    def __iand__(self, other):
        self._and_(other)
        return self
