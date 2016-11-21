from ext.attribute_packer import AttributePackerMixin


class RGBLight(AttributePackerMixin):
    _ATTRS = {'red': 0, 'green': 0, 'blue': 0}

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
        for attr_name, attr_value in self._ATTRS.items():
            setattr(self, attr_name, attr_value)

    def todict(self):
        return {attr: getattr(self, attr) for attr in self._ATTRS}

    def _and_(light1, light2):
        for light in (light1, light2):
            assert isinstance(light, RGBLight)
        for attr in self._ATTRS:
            setattr(light1, attr, max(getattr(light1, attr), getattr(light2, attr)))
    def __and__(light1, light2):
        t = copy(light1)
        t._and_(light2)
        return t
    def __iand__(self, other):
        self._and_(other)
        return self
