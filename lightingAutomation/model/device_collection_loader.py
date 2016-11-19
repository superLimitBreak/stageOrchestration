import logging
import yaml

from pysistence import make_dict

from .device_collection import DeviceCollection

from .devices.rgb_light import RGBLight
from .devices.rgb_strip_light import RGBStripLight
from .devices.effect_light import EffectRGBLight
from .devices.smoke import Smoke
from .devices.dmx_passthrough import DMXPassthru

log = logging.getLogger(__name__)

DEVICE_TYPES = make_dict({
    device_class.__name__: device_class
    for device_class in (RGBLight, RGBStripLight, EffectRGBLight, Smoke, DMXPassthru)
})


def device_collection_loader(path=None, data=None):
    assert bool(path) ^ bool(data), 'Provide either a path or data'
    if path:
        log.debug(f'Loading device_collection: {path}')
        with open(path, 'rt') as filehandle:
            data = yaml.load(filehandle)
    data = make_dict(data)

    def create_device(device_spec):
        if isinstance(device_spec, str):
            device_type = device_spec
            device_spec = {}
        else:
            device_type = device_spec.pop('device')
        assert device_type in DEVICE_TYPES, f'{device_type} is not a supported device. The valid options are {DEVICE_TYPES.keys()}'
        return DEVICE_TYPES[device_type](**device_spec)

    device_collection = DeviceCollection(make_dict({
        device_name: create_device(device_spec)
        for device_name, device_spec in data['devices'].items()
    }))

    # TODO: Possible bug?
    #   If yaml does not return ordered dict's this may fail.
    #   If pysistence does not support ordered dicts this may fail
    #   We may have to chnage the data structure to accomadate repeatable item order or build dependency order ourselfs
    for group_name, device_names in data['groups'].items():
        device_collection.add_group(group_name, device_names)

    #log.info(f'Loaded device_collection: {}'.format({})) groupby RGBLight*8 RGBStripLight*4
    return device_collection
