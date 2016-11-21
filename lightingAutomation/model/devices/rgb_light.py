from ext.attribute_packer import AttributePackerMixin


class RGBLight(AttributePackerMixin):

    def __init__(self, red=0, green=0, blue=0):
        self.red = red
        self.green = green
        self.blue = blue
        AttributePackerMixin.__init__(self, (
            AttributePackerMixin.Attribute('red', 'onebyte'),
            AttributePackerMixin.Attribute('green', 'onebyte'),
            AttributePackerMixin.Attribute('blue', 'onebyte'),
        ))

    @property
    def rgb(self):
        return (self.red, self.green, self.blue)
    @rgb.setter
    def rgb(self, rgb):
        self.red, self.green, self.blue = rgb

    def reset(self):
        self.rgb = (0, 0, 0)

    def todict(self):
        return {attr: getattr(self, attr) for attr in ('red', 'green', 'blue')}
