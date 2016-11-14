import yaml

from pysistence import make_dict

from .device_collection import DeviceCollection

from .devices.rgb_light import RGBLight
from .devices.rgb_strip_light import RGBStripLight
from .devices.effect_light import EffectRGBLight
from .devices.smoke import Smoke
from .devices.dmx_passthrough import DMXPassthru

DEVICE_TYPES = make_dict({
    device_class.__name__: device_class
    for device_class in (RGBLight, RGBStripLight, EffectRGBLight, Smoke, DMXPassthru)
})


def device_collection_loader(path=None, data=None):
    assert bool(path) ^ bool(data), 'Provide either a path or data'
    if path:
        with open(path, 'rt') as filehandle:
            data = yaml.load(filehandle)
    data = make_dict(data)

    def create_device(device_spec):
        if isinstance(device_spec, str):
            device_type = device_spec
            device_spec = {}
        else:
            device_type = device_spec.pop('device')
        return DEVICE_TYPES[device_type](**device_spec)

    device_collection = DeviceCollection(make_dict({
        device_name: create_device(device_spec)
        for device_name, device_spec in data['devices']
    }))

    for groups in data['groups']:
        for group in groups:
            for group_name, device_names in group:
                device_collection.add_group(group_name, device_names)

    return device_collection
