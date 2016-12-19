import pytest
import math
from copy import copy
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


def test_device_collection_copy(device_collection):
    device_collection.get_device('rgb_light').red = 0.1
    device_collection.get_device('rgb_strip_light_3').red = 0.2
    device_collection.get_device('rgb_effect_light').x = 0.3

    device_collection_2 = copy(device_collection)

    device_collection.get_device('rgb_light').red = 0.4
    device_collection.get_device('rgb_strip_light_3').red = 0.5
    device_collection.get_device('rgb_effect_light').x = 0.6

    assert device_collection_2.get_device('rgb_light').red == 0.1
    assert device_collection_2.get_device('rgb_strip_light_3').lights[2].red == 0.2
    assert device_collection_2.get_device('rgb_effect_light').x == 0.3


def test_device_collection_overlay(device_collection):
    device_collection_2 = copy(device_collection)

    device_collection.get_device('rgb_light').red = 0.1
    device_collection.get_device('rgb_strip_light_3').red = 0.5
    device_collection.get_device('rgb_effect_light').x = 0.3

    device_collection_2.get_device('rgb_light').red = 0.4
    device_collection_2.get_device('rgb_strip_light_3').red = 0.2
    device_collection_2.get_device('rgb_effect_light').x = 0.6

    device_collection &= device_collection_2

    assert device_collection.get_device('rgb_light').red == 0.4
    assert device_collection.get_device('rgb_strip_light_3').red == 0.5
    isclose(device_collection.get_device('rgb_effect_light').x, 0.45)


@pytest.mark.skip  # TODO: Fix this bug!
def test_device_collection_get_devices_should_protect_against_duplicates(device_collection):
    """
    Order of devices should be preserved, but duplicates should be removed
    """
    all_devices_manually = device_collection.get_devices('rgb_light', 'rgb_strip_light_3', 'rgb_strip_light_8', 'rgb_effect_light')
    all_devices_with_duplicates_from_alias = device_collection.get_devices('rgb_light', 'rgb_strip_light_3', 'rgb_strip_light_8', 'rgb_effect_light', 'all_lights')
    assert all_devices_manually == all_devices_with_duplicates_from_alias
