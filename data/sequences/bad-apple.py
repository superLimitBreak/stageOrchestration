from itertools import cycle, chain

import pytweening

from calaldees.animation.timeline import Timeline

import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *


name = __name__.split('.')[-1]
META = {
    'name': name,
    'bpm': 138,
    'timesignature': '4:4',
}


def create_timeline(dc, t, tl, el):
    #tl.set_(dc.get_device('floorLarge1'), values={'red': 0, 'green': 0, 'blue': 0})
    #tl.from_to(dc.get_devices('sidesFloor'), t('16.0.0'), {'red': 1, 'green':0}, {'red': 0, 'green': 1})

    #devices = (dc.get_device('floorLarge1'), dc.get_device('floorLarge2'))

    rhythm = (t('1.2.1'),) * 3 + (t('1.1.2'),) * 4 + (t('1.2.1'),) * 3 + (t('1.1.3'),) * 2


    #tl += sweep(dc.get_device('floorFrontBarCenter').lights, color.RED, t('1.2.1')) + sweep(reversed(dc.get_device('floorFrontBarCenter').lights), color.RED, t('1.2.1'))

    # Intro 1 ------------------------------------------------------------------
    tl_intro_1 = Timeline()
    for x in range(4):
        tl_intro_1 += light_random_state(dc.get_devices('allLights'), (color.WHITE, ), rhythm)

    # Intro 2 ------------------------------------------------------------------
    tl_intro_2 = Timeline()

    tl_intro_2 &= pop(
        dc.get_devices('rear'),
        duration_attack=t('1.1.2'),
        duration_decay=t('1.1.4'),
        valuesTo=color.WHITE,
        tween=None,
        tween_out=None
    ) * 2

    tl_intro_2 &= hard_cycle(
        dc.get_devices('front') - {dc.get_device('floorFrontBarCenter'),},
        (color.RED, color.YELLOW),
        t('1.2.1'),
    )

    RED_DARK = blend(color.BLACK, color.RED, blend=0.6)
    colors = (RED_DARK, color.RED, RED_DARK) + ((color.BLACK,) * 5)
    tl_intro_2 &= (
        light_cycle(dc.get_device('floorFrontBarCenter').lights, states=colors, duration=t('1.2.1'), tween=pytweening.easeInOutQuint)
        +
        light_cycle(dc.get_device('floorFrontBarCenter').lights, states=colors, duration=t('1.2.1'), tween=Timeline.Tween.tween_invert(pytweening.easeInOutQuint))
    )

    tl_intro_2 = tl_intro_2 * 32

    # Fuzz ---------------------------------------------------------------------
    tl_fuzz = light_random_frame_fuzz(
        devices=tuple(chain.from_iterable(strip_light.lights for strip_light in dc.get_devices('floorFrontBarLeft', 'floorFrontBarCenter', 'floorFrontBarRight'))),
        duration=t('3.1.1'),
        states=(
            color.CYAN, color.BLUE, color.MAGENTA, color.WHITE, color.YELLOW,
        )
    )

    # Main ---------------------------------------------------------------------
    tl += (
        tl_intro_1 +
        tl_intro_2 +
        tl_fuzz
    )

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": f"{name}/badApple_withClick.ogg",
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "rear",
        "func": "video.start",
        "src": f"{name}/bad-apple_original.mp4",
        "volume": 0.0,
        "position": 1.3 + 0.1,
        "timestamp": t('1.1.1')+0.1,
    })
    el.add_trigger({
        "deviceid": "front",
        "func": "video.start",
        "src": f"{name}/bad_apple_front_screen_wip1.mp4",
        "volume": 0.0,
        "position": 1.3,
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "side",
        "func": "text.html_bubble",
        "html": """
            <h1>Bad Apple</h1>
            <p>Touhou</p>
            <p>Masayoshi Minoshima and Haruka</p>
            <p>Arrangement: Joe</p>
            <p>Translation: Del</p>
        """,
        "timestamp": t('2.1.1'),
    })
    el.add_trigger({
        "deviceid": "side",
        "func": "image.show",
        "src": f"{name}/image.png",
        "timestamp": t('2.1.1'),
        "duration": t('10.1.1'),
    })
