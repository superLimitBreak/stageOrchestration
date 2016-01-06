"""
Each def renders the bytes for config.yaml/device
"""


def rgb(_, rgbw):
    return (
        rgbw[0] + rgbw[3],
        rgbw[1] + rgbw[3],
        rgbw[2] + rgbw[3],
    )


def rgb_calibrate(rgb, red_factor=1, green_factor=1, blue_factor=1, **kwargs):
    return (
        rgb[0] * red_factor,
        rgb[1] * green_factor,
        rgb[2] * blue_factor,
    )


def FlatPar(config, rgbw):
    return rgb_calibrate(rgbw, **config['device_config']['FlatPar']) + (rgbw[3], )


def neoneonfloor(config, rgbw):
    return (
        config['device_config']['neoneonfloor']['mode'],  # Constant to enter 3 light mode
        0,
    ) + neoneonfloorPart(config, rgbw)


def neoneonfloorPart(_, rgbw):
    return rgb(_, rgbw)


def OrionLinkV2(config, rgbw):
    return tuple(v + rgbw[3] for v in rgb_calibrate(rgbw, config['device_config']['OrionLinkV2']))


def OrionLinkV2Final(config, rgbw):
    return OrionLinkV2(config, rgbw) + (
        0,  # No flash
        255,  # Master dim
    )
