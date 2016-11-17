import pytest
import math
from collections import OrderedDict

from ext.attribute_packer import MemoryFramePacker, PersistentFramePacker

from lightingAutomation.model.device_collection import DeviceCollection
from lightingAutomation.model.device_collection_loader import device_collection_loader
from lightingAutomation.model.devices.rgb_light import RGBLight


def isclose(a, b):
    assert math.isclose(a, b, rel_tol=0.02)


@pytest.mark.parametrize(('packer_class',), (
    (MemoryFramePacker,),
    (PersistentFramePacker,),
))
def test_device_collection(packer_class):
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

    device_collection_frame_packer = packer_class(device_collection)

    for device in (light1, light2):
        device.red = 0.0
        device.green = 0.1
        device.blue = 0.2
    device_collection_frame_packer.save_frame()

    light1.red = 0.3
    light1.green = 0.4
    light1.blue = 0.5
    light2.red = 0.6
    light2.green = 0.7
    light2.blue = 0.8
    device_collection_frame_packer.save_frame()

    device_collection_frame_packer.restore_frame(0)
    isclose(light1.red, 0)
    isclose(light2.red, 0)
    isclose(light1.green, 0.1)
    isclose(light2.green, 0.1)
    isclose(light1.blue, 0.2)
    isclose(light2.blue, 0.2)

    device_collection_frame_packer.restore_frame(1)
    isclose(light1.red, 0.3)
    isclose(light1.green, 0.4)
    isclose(light1.blue, 0.5)
    isclose(light2.red, 0.6)
    isclose(light2.green, 0.7)
    isclose(light2.blue, 0.8)

    device_collection_frame_packer.close()


def test_device_collection_loader():
    data = {
        'devices': {
            'light1': 'RGBLight',
            'light2': {'device': 'RGBLight'},
            'lightX': {'device': 'RGBLight'},
        },
        'groups': OrderedDict((
            ('numbers', ('light1', 'light2')),
            ('letters', ('lightX',)),
            ('all', ('numbers', 'letters')),
        )),
    }
    device_collection = device_collection_loader(data=data)

    def get_device_types(devices):
        return tuple(type(device) for device in devices)
    assert get_device_types(device_collection.get_devices('light1')) == (RGBLight, )
    assert get_device_types(device_collection.get_devices('numbers')) == (RGBLight, RGBLight)
    assert get_device_types(device_collection.get_devices('all')) == (RGBLight, RGBLight, RGBLight)
