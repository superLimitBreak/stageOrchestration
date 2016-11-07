from lightingAutomation.model.device_collection import DeviceCollection
from lightingAutomation.model.devices.rgb_light import RGBLight


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
        device.red = 0
        device.green = 1
        device.blue = 2
    device_collection.save_frame()

    light1.red = 3
    light1.green = 4
    light1.blue = 5
    light2.red = 6
    light2.green = 7
    light2.blue = 8
    device_collection.save_frame()

    device_collection.restore_frame(0)
    assert light1.red == light2.red == 0
    assert light1.green == light2.green == 1
    assert light1.blue == light2.blue == 2

    device_collection.restore_frame(1)
    assert light1.red == 3
    assert light1.green == 4
    assert light1.blue == 5
    assert light2.red == 6
    assert light2.green == 7
    assert light2.blue == 8
