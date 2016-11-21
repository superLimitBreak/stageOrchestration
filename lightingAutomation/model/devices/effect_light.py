from enum import Enum

from ext.attribute_packer import AttributePackerMixin

from .rgb_light import RGBLight

GLOBOS = Enum('Globo', ('none', 'cross', 'dots', 'crescent_moon', 'target', 'triangle', 'square', 'stars'))

class EffectRGBLight(RGBLight):

    def __init__(self, *args, x=0, y=0, globo=GLOBOS.none, globo_rotation=0, **kwargs):
        super().__init__(*args, **kwargs)
        self.x = x
        self.y = y
        self.globo = globo
        self.globo_rotation = globo_rotation
        AttributePackerMixin.__init__(self, (
            AttributePackerMixin.Attribute('x', 'onebyte'),
            AttributePackerMixin.Attribute('y', 'onebyte'),
            AttributePackerMixin.Attribute('globo', 'byte'),
            AttributePackerMixin.Attribute('globo_rotation', 'plusminusonebyte'),
        ))

    def reset(self):
        super().reset()
        self.x = 0
        self.y = 0
        self.globo = GLOBOS.none
        self.globo_rotation = 0

    def todict(self):
        d = super().todict()
        d.update({attr: getattr(self, attr) for attr in ('x', 'y', 'globo', 'globo_rotation')})
        return d
