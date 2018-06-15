from statistics import mean
from enum import Enum

from calaldees.attribute_packer import AttributePackerMixin

from . import RGBLight
from ._base import BaseDevice

GLOBOS = Enum('Globo', ('none', 'cross', 'dots', 'crescent_moon', 'target', 'triangle', 'square', 'stars'))

_mean = lambda a, b: mean((a, b))


AttributePackerMixin.AttributeEncoders['globo'] = AttributePackerMixin.AttributeEncoder(
    lambda value: value.value,
    lambda value: GLOBOS(value),
    'B',
)


class EffectRGBLight(RGBLight):

    def __init__(self, *args, x=0.5, y=0.5, globo=GLOBOS.none, globo_rotation=0, device_attributes=(), **kwargs):
        self.x = x
        self.y = y
        self.globo = globo
        self.globo_rotation = globo_rotation
        super().__init__(*args, device_attributes=(
            BaseDevice.DeviceAttribute(name='x', default=x, and_func=_mean, packer_type='onebyte'),
            BaseDevice.DeviceAttribute(name='y', default=y, and_func=_mean, packer_type='onebyte'),
            BaseDevice.DeviceAttribute(name='globo', default=globo, and_func=lambda a, b: a, packer_type='globo'),
            BaseDevice.DeviceAttribute(name='globo_rotation', default=globo_rotation, and_func=_mean, packer_type='plusminusonebyte'),
        ) + device_attributes, **kwargs)

    def __copy__(self):
        return EffectRGBLight(**self.todict())

    def _and_(light1, light2):
        for light in (light1, light2):
            assert isinstance(light, EffectRGBLight)
        RGBLight._and_(light1, light2)
