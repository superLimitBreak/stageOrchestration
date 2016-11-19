from lightingAutomation.output.realtime.json import _render_json

def test_output_json(device_collection):
    device_collection.get_device('rgb_light').red = 0.5
    device_collection.get_device('rgb_strip_light_3').red = 0.6
    device_collection.get_device('rgb_effect_light').x = 0.7

    _render_json(device_collection) == {

    }
