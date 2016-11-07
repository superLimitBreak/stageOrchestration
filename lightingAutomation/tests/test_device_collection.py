import math

from lightingAutomation.lightingAutomation.model.device_collection import DeviceCollection
from lightingAutomation.lightingAutomation.model.devices.rgb_light import RGBLight


def isclose(a, b):
    assert math.isclose(a, b, rel_tol=0.02)


def test_device_collection():
    light1 = RGBLight()
    light2 = RGBLight()
    device_collection = DeviceCollection({
        'light1': light1,
        'light2': light2,
    })
    device_collection.add_group('all', ('light1', 'light2'))

    assert device_collection.get_devices('light1') == (light1, )
    assert device_collection.get_devices('light2') == (light2, )
    assert device_collection.get_devices('all') == (light1, light2)

    for device in (light1, light2):
        device.red = 0.0
        device.green = 0.1
        device.blue = 0.2
    device_collection.save_frame()

    light1.red = 0.3
    light1.green = 0.4
    light1.blue = 0.5
    light2.red = 0.6
    light2.green = 0.7
    light2.blue = 0.8
    device_collection.save_frame()

    device_collection.restore_frame(0)
    isclose(light1.red, 0)
    isclose(light2.red, 0)
    isclose(light1.green, 0.1)
    isclose(light2.green, 0.1)
    isclose(light1.blue, 0.2)
    isclose(light2.blue, 0.2)

    device_collection.restore_frame(1)
    isclose(light1.red, 0.3)
    isclose(light1.green, 0.4)
    isclose(light1.blue, 0.5)
    isclose(light2.red, 0.6)
    isclose(light2.green, 0.7)
    isclose(light2.blue, 0.8)
