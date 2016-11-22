from ext.misc import freeze

from unittest.mock import Mock

from lightingAutomation.model.devices.effect_light import GLOBOS
from lightingAutomation.output.realtime.json import _render_json, RealtimeOutputJSON


def test_output_json(device_collection):
    device_collection.get_device('rgb_light').red = 0.5
    device_collection.get_device('rgb_strip_light_3').red = 0.6
    device_collection.get_device('rgb_effect_light').x = 0.7
    device_collection.get_device('rgb_effect_light').globo = GLOBOS.dots

    assert _render_json(device_collection) == {
        'rgb_light': {'red': 0.5, 'green': 0, 'blue': 0},
        'rgb_strip_light_3': ({'red': 0.6, 'green': 0, 'blue': 0},) * 3,
        'rgb_strip_light_8': ({'red': 0, 'green': 0, 'blue': 0},) * 8,
        'rgb_effect_light': {'red': 0, 'green': 0, 'blue': 0, 'x': 0.7, 'y': 0, 'globo': GLOBOS.dots, 'globo_rotation': 0},
    }


def test_output_json_object(device_collection):
    json_send_function = Mock()
    output = RealtimeOutputJSON(device_collection, json_send_function)
    device_collection.get_device('rgb_light').red = 0.8
    output.update()
    json_send_function.assert_called_once()
    assert json_send_function.call_args[0][0]['rgb_light']['red'] == 0.8
