from ext.attribute_packer import CollectionPackerMixin


class DeviceArray(CollectionPackerMixin):
    """
    A collection of lights with positions.
    This models the stage layout and devices
    """
    def __init__(self):
        CollectionPackerMixin.__init__(self, xx)
