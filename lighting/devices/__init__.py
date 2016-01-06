"""
Each def renders the bytes for config.yaml/device
"""


def lightRGBW(config, rgbw):
    return (
        rgbw[0] * config['device_config']['lightRGBW']['red_factor'],
        rgbw[1] * config['device_config']['lightRGBW']['green_factor'],
        rgbw[2] * config['device_config']['lightRGBW']['blue_factor'],
        rgbw[3]
    )
