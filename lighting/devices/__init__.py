"""
Each def renders the bytes for config.yaml/device
"""


# Utils ------------------------------------------------------------------------

def rgb_calibrate(rgb, red_factor=1, green_factor=1, blue_factor=1, **kwargs):
    return (
        rgb[0] * red_factor,
        rgb[1] * green_factor,
        rgb[2] * blue_factor,
    )


# Devices ----------------------------------------------------------------------

def FlatPar(config, rgb):
    device_config = config['device_config']['FlatPar']
    # WHITE_FACTOR = device_config['white_factor']   # Broken and will only work for WHITE_FACTOR 0.5. FIX THIS
    rgb = rgb_calibrate(rgb, **device_config)
    w = rgb[3]
    #def white_factor(w, factor_key):
    #    if w > WHITE_FACTOR:
    #        return ((w-WHITE_FACTOR)/(1-WHITE_FACTOR)) * (1-device_config[factor_key])
    #    else:
    #        return 0
    return (
        rgb[0],  # white_factor(w, 'red_factor'),
        rgb[1],  # white_factor(w, 'green_factor'),
        rgb[2],  # white_factor(w, 'blue_factor'),
        w,  # / WHITE_FACTOR,
    )


def neoneonfloor(config, rgb):
    return (
        0.196,  # Constant to enter 3 light mode - this float translates to the byte value of '50'
        0,
    ) + neoneonfloorPart(config, rgb)


def neoneonfloorPart(_, rgb):
    return rgb


def OrionLinkV2(config, rgb):
    return tuple(v for v in rgb_calibrate(rgb, **config['device_config']['OrionLinkV2']))


def OrionLinkV2Final(config, rgb):
    return OrionLinkV2(config, rgb) + (
        0,  # No flash
        1,  # Master dim - the value '1' (max) is transformed to byte '255'
    )


def cauvetHuricane(config, data):
    """
    2 byte device (Fan speed, Smoke)
    6 is the minimum fan speed to activate the system
    """
    try:
        # Please remove this hack. It was to facilitate midi control in a hurry
        data = data.__iter__().__next__()
    except AttributeError:
        pass
    return (6/255, float(data))
