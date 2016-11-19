import pytest

from lightingAutomation.model.devices import RGBLight, RGBStripLight, EffectRGBLight, Smoke
import lightingAutomation.output.realtime.dmx.dmx_devices as dmx_devices


@pytest.mark.parametrize(('dmx_device_name', 'device', 'expected_bytes'), (
    ('FlatPar', RGBLight(red=1.0, green=1.0, blue=1.0), bytes((255, 71, 186, 255))),
    ('neoNeonFloorSmall', RGBStripLight(3, red=1.0, green=0.5, blue=0.75), bytes((50, 0)) + bytes((255, 127, 191)) * 3 ),
    ('OrionLinkV2', RGBStripLight(8, red=1.0, green=1.0, blue=1.0), bytes((255, 76, 127)) * 8 + bytes((0, 255))),
    #('cauvetHuricane', ),
    #('EuroLight200', ),
))
def test_dmx_devices(dmx_device_name, device, expected_bytes):
    assert getattr(dmx_devices, dmx_device_name)(device) == expected_bytes, \
        f'{dmx_device_name} should produce {expected_bytes}'
