from collections import namedtuple

from ext.attribute_packer import AttributePackerMixin


class BaseDevice(AttributePackerMixin):
    DeviceAttribute = namedtuple('Attribute', ('name', 'default', 'and_func', 'packer_type'))

    def __init__(self, device_attributes):
        self.device_attributes = device_attributes
        AttributePackerMixin.__init__(self, (
            AttributePackerMixin.Attribute(device_attribute.name, device_attribute.packer_type)
            for device_attribute in device_attributes
        ))

    def reset(self):
        for device_attribute in self.device_attributes:
            setattr(self, device_attribute.name, device_attribute.default)

    def todict(self):
        return {
            device_attribute.name: getattr(self, device_attribute.name)
            for device_attribute in self.device_attributes
        }

    def _and_(device1, device2):
        for device in (device1, device2):
            assert isinstance(device, BaseDevice)
        for device_attribute in device1.device_attributes:
            setattr(
                device1,
                device_attribute.name,
                device_attribute.and_func(
                    getattr(device1, device_attribute.name),
                    getattr(device2, device_attribute.name),
                )
            )

    def __and__(device1, device2):
        device1 = copy(device1)
        device._and_(device2)
        return device

    def __iand__(self, other):
        self._and_(other)
        return self
