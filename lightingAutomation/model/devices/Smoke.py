from ext.attribute_packer import AttributePackerMixin


class Smoke(AttributePackerMixin):
    def __init__(self, smoke=0, fan=0):
        self.smoke = smoke
        self.fan = fan
        AttributePackerMixin.__init__(self, (
            AttributePackerMixin.Attribute('smoke', 'onebyte'),
            AttributePackerMixin.Attribute('fan', 'onebyte'),
        ))
