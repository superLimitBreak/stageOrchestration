from calaldees.attribute_packer import AttributePackerMixin


class DMXPassthru(AttributePackerMixin):
    """
    A stub for manipulating dmx bytes directly.
    This could be due to interacting with a device that was not known in development
    or low level testing of DMX devices
    """
    pass  # Unimplemented
