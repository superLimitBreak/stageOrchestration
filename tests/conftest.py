import pytest

from lightingAutomation.model.device_collection_loader import device_collection_loader


@pytest.fixture(scope="function")
def device_collection():
    return device_collection_loader(data={
        'devices': {
            'rgb_light': 'RGBLight',
            'rgb_strip_light_3': {'device': 'RGBStripLight', 'size': 3},
            'rgb_strip_light_8': {'device': 'RGBStripLight', 'size': 8},
            'rgb_effect_list': 'RGBEffectLight',
        },
    })
