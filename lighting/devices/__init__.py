"""
Each def renders the bytes for config.yaml/device
"""


def rgbw_to_rgb(_, rgbw):
    return (
        rgbw[0] + rgbw[3],
        rgbw[1] + rgbw[3],
        rgbw[2] + rgbw[3],
    )


def rgb_calibrate(rgb, red_factor=1, green_factor=1, blue_factor=1):
    return (
        rgb[0] * red_factor,
        rgb[1] * green_factor,
        rgb[2] * blue_factor,
    )


def FlatPar(config, rgbw):
    WHITE_FACTOR = 0.5
    device_config = config['device_config']['FlatPar']
    rgb = rgb_calibrate(rgbw, **device_config)
    w = rgbw[3]
    def white_factor(w, factor_key):
        if w > WHITE_FACTOR:
            return (w-WHITE_FACTOR) * (1/WHITE_FACTOR) * (1-device_config[factor_key])
        else:
            return 0
    return (
        rgb[0] + white_factor(w, 'red_factor'),
        rgb[1] + white_factor(w, 'green_factor'),
        rgb[2] + white_factor(w, 'blue_factor'),
        w * (1/WHITE_FACTOR),
    )


def neoneonfloor(config, rgbw):
    return (
        config['device_config']['neoneonfloor']['mode'],  # Constant to enter 3 light mode
        0,
    ) + neoneonfloorPart(config, rgbw)


def neoneonfloorPart(_, rgbw):
    return rgbw_to_rgb(_, rgbw)


def OrionLinkV2(config, rgbw):
    return tuple(v + rgbw[3] for v in rgb_calibrate(rgbw, **config['device_config']['OrionLinkV2']))


def OrionLinkV2Final(config, rgbw):
    return OrionLinkV2(config, rgbw) + (
        0,  # No flash
        255,  # Master dim
    )
