from copy import copy
from collections import OrderedDict
from itertools import chain

from pysistence import make_dict

from ext.attribute_packer import CollectionPackerMixin, BasePackerMixin, MemoryFramePacker


class DeviceCollection(CollectionPackerMixin):

    def __init__(self, devices):
        self._devices = make_dict(devices)
        CollectionPackerMixin.__init__(self, tuple(self._devices.values()))  # TODO: Unless we can guarantee the order of values, this approach is flawed
        self._group_lookup = {device_name: (device_name, ) for device_name in self._devices.keys()}
        self.reset()

    def add_group(self, group_name, device_names):
        self._group_lookup[group_name] = tuple(chain(*(
            self._group_lookup[device_name] for device_name in device_names
        )))

    def get_device(self, name):
        return self._devices.get(name)

    def get_devices(self, name):
        return tuple(
            self.get_device(device_name)
            for device_name in self._group_lookup.get(name, ())
        )

    def reset(self):
        for device in self._devices.values():
            device.reset()

    def todict(self):
        return {device_name: device.todict() for device_name, device in self._devices.items()}

    def __copy__(self):
        device_collection = DeviceCollection({name: copy(device) for name, device in self._devices.items()})
        device_collection._group_lookup = copy(self._group_lookup)
        return device_collection
