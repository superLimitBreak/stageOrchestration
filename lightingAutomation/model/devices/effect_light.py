from enum import Enum

from ext.attribute_packer import AttributePackerMixin

from .rgb_light import RGBLight

GLOBOS = Enum('Globo', ('none', 'cross', 'dots', 'crescent_moon', 'target', 'triangle', 'square', 'stars'))


class EffectRGBLight(RGBLight):
    _ATTRS = dict(**RGBLight._ATTRS, **{'x': 0, 'y': 0, 'globo': GLOBOS.none, 'globo_rotation': 0})

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

    def __copy__(self):
        return EffectRGBLight(**self.todict())

    def _and_(light1, light2):
        for light in (light1, light2):
            assert isinstance(light, EffectRGBLight)
        super()._and_(light1, light2)
