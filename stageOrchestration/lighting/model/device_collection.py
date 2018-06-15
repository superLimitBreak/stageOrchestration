from copy import copy
from collections import OrderedDict
from itertools import chain

from pysistence import make_dict

from calaldees.attribute_packer import CollectionPackerMixin, BasePackerMixin, MemoryFramePacker


DEVICE_REQUIRED_ATTRS = ('__iand__', '__and__', '__copy__')


class DeviceCollection(CollectionPackerMixin):

    def __init__(self, devices):
        for device_name, device in devices.items():
            for attr in DEVICE_REQUIRED_ATTRS:
                assert hasattr(device, attr), f'{deivce_name} does not support the mandatory {attr}'
        self._devices = make_dict(devices)
        CollectionPackerMixin.__init__(self, tuple(self._devices.values()))  # TODO: Unless we can guarantee the order of values, this approach is flawed
        self._group_lookup = {device_name: (device_name, ) for device_name in self._devices.keys()}

    @property
    def groups(self):
        return self._group_lookup.keys()

    @property
    def devices(self):
        return self._devices.keys()

    def add_group(self, group_name, device_names):
        self._group_lookup[group_name] = tuple(chain(*(
            self._group_lookup[device_name] for device_name in device_names
        )))

    def get_device(self, name):
        return self._devices.get(name)

    def get_devices(self, *names):
        if names:
            devices_generator = (
                self.get_device(device_name)
                for name in names
                for device_name in self._group_lookup.get(name, ())
            )
            devices_set = set()
            def dedupe(device):
                if device not in devices_set:
                    devices_set.add(device)
                    return True
            return tuple(filter(dedupe, devices_generator))
        return self._devices.values()

    def reset(self):
        for device in self._devices.values():
            device.reset()

    def todict(self):
        return {device_name: device.todict() for device_name, device in self._devices.items()}

    def __copy__(self):
        device_collection = DeviceCollection({name: copy(device) for name, device in self._devices.items()})
        device_collection._group_lookup = copy(self._group_lookup)
        return device_collection

    def _and_(device_collection_1, device_collection_2):
        for device_collection in (device_collection_1, device_collection_2):
            assert isinstance(device_collection, DeviceCollection)
        assert device_collection_1._devices.keys() == device_collection_2._devices.keys(), 'Can only merge collections that have the same devices'
        for device_name, device in device_collection_2._devices.items():
            device_collection_1._devices[device_name]._and_(device)
    def __and__(device_collection_1, device_collection_2):
        dc = copy(device_collection_1)
        dc._and_(device_collection_2)
        return dc
    def __iand__(self, other):
        self._and_(other)
        return self
