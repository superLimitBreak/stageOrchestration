from ext.misc import freeze

from lightingAutomation.output.realtime.json import _render_json

def test_output_json(device_collection):
    device_collection.get_device('rgb_light').red = 0.5
    device_collection.get_device('rgb_strip_light_3').red = 0.6
    device_collection.get_device('rgb_effect_light').x = 0.7

    assert _render_json(device_collection) == {
        'rgb_light': {'red': 0.5, 'green': 0, 'blue': 0},
        'rgb_strip_light_3': ({'red': 0.6, 'green': 0, 'blue': 0},) * 3,
        'rgb_strip_light_8': ({'red': 0, 'green': 0, 'blue': 0},) * 8,
        'rgb_effect_light': {'red': 0, 'green': 0, 'blue': 0, 'x': 0.7, 'y': 0, 'globo': 1, 'globo_rotation': 0},
    }
