from ext.attribute_packer import AttributePackerMixin

from ._base_device import BaseDevice


class DMXPassthru(BaseDevice):
    """
    A stub for manipulating dmx bytes directly.
    This could be due to interacting with a device that was not known in development
    or low level testing of DMX devices
    """
    pass  # Unimplemented
