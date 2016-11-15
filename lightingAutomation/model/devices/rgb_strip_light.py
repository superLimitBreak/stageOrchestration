from ext.attribute_packer import CollectionPackerMixin
from .rgb_light import RGBLight


class RGBStripLight(CollectionPackerMixin):
    def __init__(self, size):
        self.lights = tuple(RGBLight() for i in range(size))
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
    def _red_setter(self, value):
        self._set_group_attr('red', value)

    @property
    def green(self):
        return self._average_attr('green')
    @green.setter
    def _green_setter(self, value):
        self._set_group_attr('green', value)

    @property
    def blue(self):
        return self._average_attr('blue')
    @blue.setter
    def _blue_setter(self, value):
        self._set_group_attr('blue', value)
