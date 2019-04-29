from pytweening import easeInOutQuint

from calaldees.animation.timeline import Timeline

import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *

META = {
    'name': 'Test of tests',
    'bpm': 138,
    'timesignature': '4:4',
}


from calaldees.data import get_index_float_blend, set_attr_or_item_all, blend


def light_cycle(devices, colors, duration, tween=Timeline.Tween.tween_linear):
    colors = tuple(colors)

    def render_item_func(pos):
        for device_index, device in enumerate(devices):
            set_attr_or_item_all(
                source=get_index_float_blend(device_index + (pos * len(devices)), colors),
                target=device,
            )

    t = Timeline()
    t.animation_item(0, duration, render_item_func, tween)
    return t


def create_timeline(dc, t, tl, el):
    #tl.set_(dc.get_device('floorLarge1'), values={'red': 0, 'green': 0, 'blue': 0})
    #tl.from_to(dc.get_devices('sidesFloor'), t('16.0.0'), {'red': 1, 'green':0}, {'red': 0, 'green': 1})

    #devices = (dc.get_device('floorLarge1'), dc.get_device('floorLarge2'))

    tl &= pop(dc.get_devices('rear'), duration_attack=t('1.1.2'), duration_decay=t('1.1.4'), valuesTo=color.WHITE, tween=None, tween_out=None) * 2
    tl &= hard_cycle(dc.get_devices('front') - {dc.get_device('floorFrontBarCenter'),}, (color.RED, color.YELLOW), t('1.2.1'))
    #tl += sweep(dc.get_device('floorFrontBarCenter').lights, color.RED, t('1.2.1')) + sweep(reversed(dc.get_device('floorFrontBarCenter').lights), color.RED, t('1.2.1'))
    RED_DARK = blend(color.BLACK, color.RED, blend=0.6)
    colors = (RED_DARK, color.RED, RED_DARK) + ((color.BLACK,) * 5)
    tl &= (
        light_cycle(dc.get_device('floorFrontBarCenter').lights, colors=colors, duration=t('1.2.1'), tween=easeInOutQuint)
        +
        light_cycle(dc.get_device('floorFrontBarCenter').lights, colors=colors, duration=t('1.2.1'), tween=Timeline.Tween.tween_invert(easeInOutQuint))
    )

    tl = tl * 24

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": "bad-apple/badApple_withClick.ogg",
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "rear",
        "func": "video.start",
        "src": "bad-apple/bad-apple_original.mp4",
        "volume": 0.0,
        "position": 1.3,
        "timestamp": t('1.1.1'),
    })

    return tl