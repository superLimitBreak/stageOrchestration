from collections import namedtuple

from ext.attribute_packer import AttributePackerMixin


Attribute = namedtuple('Attribute', ('default', 'and_func'))

class RGBLight(AttributePackerMixin):
    _ATTRS = {
        'red': Attribute(default=0, and_func=max),
        'green': Attribute(default=0, and_func=max),
        'blue': Attribute(default=0, and_func=max),
    }

    def __init__(self, red=0, green=0, blue=0):
        self.red = red
        self.green = green
        self.blue = blue
        AttributePackerMixin.__init__(self, (
            AttributePackerMixin.Attribute('red', 'onebyte'),
            AttributePackerMixin.Attribute('green', 'onebyte'),
            AttributePackerMixin.Attribute('blue', 'onebyte'),
        ))

    def __copy__(self):
        return RGBLight(**self.todict())

    @property
    def rgb(self):
        return (self.red, self.green, self.blue)
    @rgb.setter
    def rgb(self, rgb):
        self.red, self.green, self.blue = rgb

    def reset(self):
        for attr_name, attr_spec in self._ATTRS.items():
            setattr(self, attr_name, attr_spec.default)

    def todict(self):
        return {attr: getattr(self, attr) for attr in self._ATTRS}

    def _and_(light1, light2):
        for light in (light1, light2):
            assert isinstance(light, RGBLight)
        for attr_name, attr_spec in light1._ATTRS.items():
            setattr(light1, attr_name, attr_spec.and_func(getattr(light1, attr_name), getattr(light2, attr_name)))
    def __and__(light1, light2):
        light = copy(light1)
        light._and_(light2)
        return light
    def __iand__(self, other):
        self._and_(other)
        return self
