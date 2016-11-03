from ext.attribute_packer import CollectionPackerMixin
from .rgb_light import RGBLight


class RGBStripLight(CollectionPackerMixin):
    def __init__(self, count):
        self.lights = tuple(RGBLight() for i in range(count))
        CollectionPackerMixin.__init__(self, self.lights)
