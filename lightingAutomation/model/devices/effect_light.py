from statistics import mean
from enum import Enum

from ext.attribute_packer import AttributePackerMixin

from .rgb_light import RGBLight, Attribute

GLOBOS = Enum('Globo', ('none', 'cross', 'dots', 'crescent_moon', 'target', 'triangle', 'square', 'stars'))

_mean = lambda a, b: mean((a, b))

class EffectRGBLight(RGBLight):
    _ATTRS = dict(**RGBLight._ATTRS, **{
        'x': Attribute(default=0, and_func=_mean),
        'y': Attribute(default=0, and_func=_mean),
        'globo': Attribute(default=GLOBOS.none, and_func=lambda a, b: a),
        'globo_rotation': Attribute(default=0, and_func=_mean),
    })

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
        RGBLight._and_(light1, light2)
