from ._base import BaseDevice


class RGBLight(BaseDevice):

    def __init__(self, red=0, green=0, blue=0, device_attributes=()):
        self.red = red
        self.green = green
        self.blue = blue
        super().__init__((
            BaseDevice.DeviceAttribute(name='red', default=0, and_func=max, packer_type='onebyte'),
            BaseDevice.DeviceAttribute(name='green', default=0, and_func=max, packer_type='onebyte'),
            BaseDevice.DeviceAttribute(name='blue', default=0, and_func=max, packer_type='onebyte'),
        ) + device_attributes)

    def __copy__(self):
        return RGBLight(**self.todict())

    @property
    def rgb(self):
        return (self.red, self.green, self.blue)
    @rgb.setter
    def rgb(self, rgb):
        self.red, self.green, self.blue = rgb

