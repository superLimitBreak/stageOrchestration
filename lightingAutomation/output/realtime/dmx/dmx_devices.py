from itertools import chain

from ext.misc import one_to_limit


def FlatPar(rgb_light):
    return bytes(
        one_to_limit(value, limit=255)
        for value in (
            rgb_light.red,  # * 1.0
            rgb_light.green * 0.28,
            rgb_light.blue * 0.73,
            min(rgb_light.rgb),
        )
    )


def neoNeonFloorSmall(rgb_strip_light):
    assert len(rgb_strip_light.lights) == 3
    return bytes(chain(*(
        (50, 0),  # '50' is a constant for 3 light mode
        (rgb_light.rgb for rgb_light in rgb_strip_light.lights)
    )))


def OrionLinkV2(rgb_strip_light):
    assert len(rgb_strip_light.lights) == 8
    return bytes(chain(*(
        (
            (
                one_to_limit(value, limit=255)
                for value in (
                    rgb_light.red,  # * 1.0
                    rgb_light.green * 0.3,
                    rgb_light.blue * 0.5,
                )
            )
            for rgb_light in rgb_strip_light.lights
        )
        (
            0,  # No flash
            255,  # Master dim
        )
    )))


def cauvetHuricane(smoke):
    pass
