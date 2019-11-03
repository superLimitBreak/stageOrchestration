from functools import partial
from itertools import zip_longest

from calaldees.timecode import timecode_to_seconds
from calaldees.animation.timeline import Timeline

import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *


name = __name__.split('.')[-1]
META = {
    'name': name,
    'bpm': 192,
    'timesignature': '4:4',
}

def create_timeline(dc, t, tl, el):
    tl.set_(dc.get_devices(), color.YELLOW, 0)
    tl.set_(dc.get_devices(), color.YELLOW, 275)

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": f"{name}/allan_practice_backing.ogg",
        "timestamp": t('1.1.1'),
    })
    # el.add_trigger({
    #     "deviceid": "front",
    #     "func": "video.start",
    #     "src": f"{name}/front.mp4",
    #     "volume": 0.0,
    #     "position": 0,
    #     "timestamp": t('1.1.1'),
    # })
    el.add_trigger({
        "deviceid": "side",
        "func": "text.html_bubble",
        "html": f"""
            <h1>Bloody Tears</h1>
            <p>Castelvania</p>
            <p>Kinuyo Yamashita, Satoe Terashima, Inspired by: SSH</p>
            <p>Arrangement: Joe</p>
        """,
        "timestamp": t('4.1.1'),
    })

    el.add_trigger({
        "deviceid": "side",
        "func": "image.show",
        "src": f"castelvania/castelvania1/title.gif",
        "duration": t('40.1.1'),
        "timestamp": t('10.1.1'),
    })



    # Background Scroll --------------------------------------------------------

    t2 = partial(timecode_to_seconds, bpm=232)
    T2_START = 61.8
    DEFAULT_DURATION = t2('2.1.1')
    DEFAULT_X_DIFF = 50


    # https://www.finalfantasykingdom.net/castlevania.php
    # https://castlevania.fandom.com/wiki/Games
    # https://www.spriters-resource.com/nes/castlevania3draculascurse/?source=genre
    IMAGES = {
        'cmap1': {"src": "castelvania/castelvania1/cmap1.png", "width": 3600, "height": 350},
        'cmap2': {"src": "castelvania/castelvania1/cmap2.png", "width": 2050, "height": 725},
        'cmap3': {"src": "castelvania/castelvania1/cmap3.png", "width": 3600, "height": 600},
        'cmap4': {"src": "castelvania/castelvania1/cmap4.png", "width": 4000, "height": 400},
        'cmap5': {"src": "castelvania/castelvania1/cmap5.png", "width": 2300, "height": 750},
        'cmap6': {"src": "castelvania/castelvania1/cmap6.png", "width": 3100, "height": 550},
        'c3clock': {"src": "castelvania/castelvania3/clocktowerofuntimelydeath.png", "width": 1024, "height": 2688},
        'c3forest': {"src": "castelvania/castelvania3/madforest.png", "width": 3584, "height": 992},
        'c3sunkcity': {"src": "castelvania/castelvania3/sunkencityofpoltergeist.png", "width": 3584, "height": 800},
        'c3tower': {"src": "castelvania/castelvania3/towerofterror.png", "width": 768, "height": 2688},
        'c3village': {"src": "castelvania/castelvania3/warakiyavillage.png", "width": 4096, "height": 864},
        'c3cave': {"src": "castelvania/castelvania3/alucardscave.png", "width": 4608, "height": 608},
        'c3causeway': {"src": "castelvania/castelvania3/causeway.png", "width": 3840, "height": 416},
        'c3ship': {"src": "catselvania/castelvania3/hauntedshipoffools.png", "width": 2816, "height": 768},
        'c3marsh': {"src": "catselvania/castelvania3/murkymarshofmorbidmoron.png", "width": 3840, "height": 768},
        'c3_1a': {"src": "castelvania/castelvania3/1aundergroundcatacombs.png", "width": 1792, "height": 768},
        'c3_1b': {"src": "castelvania/castelvania3/1bcastlecourtyard.png", "width": 2816, "height": 864},
        'c3_2': {"src": "castelvania/castelvania3/2cliffsideentrance.png", "width": 2048, "height": 2784},
        'c3_3': {"src": "castelvania/castelvania3/3mainhall.png", "width": 2560, "height": 768},
        'c3_4': {"src": "castelvania/castelvania3/4innerhalls.png", "width": 1280, "height": 2592},
        'c3_5': {"src": "castelvania/castelvania3/5castlekeep.png", "width": 2304, "height": 1104},
    }

    def clear_scroll(timestamp, d=1, _duration=DEFAULT_DURATION):
        el.add_trigger({
            "deviceid": "rear",
            "func": "image.empty",
            "timestamp": timestamp,
        })
        return timestamp + (d * _duration)
    def scroll(image_name, timestamp=0, d=1, x=0, y=0, x_diff=DEFAULT_X_DIFF, y_diff=0, _duration=DEFAULT_DURATION):
        trigger = {
            "deviceid": "rear",
            "func": "image.start",
            "source_screen_height": 192,
            "className": "pixelated",
            "gsap_animation": [
                ["to", 0, {"x": -x, "y": -y, "ease":"linear", "force3D": False}],
                ["to", d * _duration, {
                    "x": -x -(x_diff * d) if x_diff else -x,
                    "y": -y -(y_diff * d) if y_diff else -y,
                    "ease":"linear",
                }]
            ],
            "timestamp": timestamp,
        }
        trigger.update(IMAGES[image_name])
        el.add_trigger(trigger)
        return timestamp + (d * _duration)

    scroll('cmap1', timestamp=1, x=0, y=0, x_diff=480, _duration=58)


    RIGHT = dict(x_diff=DEFAULT_X_DIFF, y_diff=0)
    LEFT = dict(x_diff=-DEFAULT_X_DIFF, y_diff=0)
    UP = dict(x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    DOWN = dict(x_diff=0, y_diff=DEFAULT_X_DIFF/2)
    PATHS = [
        ('cmap1', 768, 0, RIGHT),
        ('cmap1', 2295, 0, RIGHT),
        ('cmap1', 2320, 163, RIGHT),
        ('cmap1', 2800, 0, RIGHT),
        ('cmap2', 160, 0, LEFT),
        ('cmap4', 2975, 0, RIGHT),
        ('cmap3', 1157, 67, RIGHT),
        ('cmap4', 6, 175, RIGHT),
        ('cmap5', 736, 0, LEFT),
        ('cmap4', 1438, 0, RIGHT),
        ('cmap5', 750, 335, RIGHT),
        ('cmap6', 2832, 368, LEFT),
        ('cmap5', 2000, 174, LEFT),
        ('cmap6', 1275, 350, UP),
        ('cmap2', 458, 4, LEFT),
        ('cmap6', 954, 190, DOWN),
        ('c3_3', 1024, 192, RIGHT),
        ('cmap6', 554, 0, LEFT),
        ('c3_1a', 896, 383, LEFT),
        ('c3clock', 768, 719, UP),
        ('c3tower', 255, 2315, UP),
        ('c3forest', 2560, 415, RIGHT),
        ('c3sunkcity', 3327, 414, LEFT),
        ('c3_1b', 2302, 238, DOWN),
        ('c3cave', 2847, 31, RIGHT),
        ('c3_5', 1791, 912, LEFT),
        ('c3tower', 511, 1583, UP), # short
        ('c3cave', 4192, 224, LEFT),
        ('c3_4', 160, 2208, RIGHT),
        ('c3cave', 3454, 224, LEFT),
        ('c3causeway', 2545, 0, RIGHT),
        ('c3_4', 1024, 2014, LEFT),
        ('c3tower', 0, 0, RIGHT),
        ('c3_4', 540, 184, LEFT),
        (None, None, None, None),
        ('c3cave', 2719, 414, LEFT),
        ('c3causeway', 0, 0, RIGHT),
        ('c3tower', 0, 662, RIGHT),
        ('c3causeway', 1000, 0, RIGHT),
        ('c3_5', 2050, 0, LEFT),
        ('c3clock', 256, 2480, UP),
        ('c3clock', 0, 1583, RIGHT),
        ('c3forest', 0, 224, RIGHT),
        ('c3_4', 768, 1118, UP),
        ('c3_1a', 1522, 576, LEFT),

        ('c3_1b', 2335, 672, RIGHT),
        ('c3cave', 318, 222, LEFT),
        ('c3_1a', 512, 192, RIGHT),
        ('c3_1b', 1792, 0, RIGHT),
        ('c3sunkcity', 3327, 414, LEFT),
        ('c3_1b', 32, 383, RIGHT),
        ('c3_2', 1024, 2014, UP),
        ('c3_2', 1320, 1342, LEFT),
        ('c3village', 1800, 192, RIGHT),
        ('c3_2', 0, 0, RIGHT),
        ('c3_3', 0, 574, RIGHT),

        ('c3forest', 2304, 604, RIGHT),
        ('c3_4', 512, 1818, UP),

        ('c3_4', 354, 0, LEFT),
        ('c3clock', 511, 910, RIGHT),

        ('c3_5', 580, 686, LEFT),

        ('c3village', 0, 672, RIGHT),
        ('c3village', 768, 480, UP),
        #('cmap2', 0, 160, RIGHT),
        ('c3_2', 0, 1084, UP), # short

        ('c3village', 1038, 192, RIGHT),  # broken?
    ]
    DURATIONS = [
        8, 4, 4, 2, 2, 1, 1, 2, 4, 4, 2, 2, 2, 1, 0.5, 0.25, 0.25, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        8,
        4, 4, 4, 4, 2,
        8, 8, 6, 6, 2,
    ]
    _next = T2_START
    for (_map, x, y, direction), duration in zip_longest(PATHS, DURATIONS, fillvalue=16):
        if not _map:
            _next = clear_scroll(timestamp=_next, d=duration)
        else:
            _next = scroll(_map, timestamp=_next, d=duration, x=x, y=y, **direction)


    el.add_trigger({
        "deviceid": "rear",
        "func": "image.show",
        "src": f"castelvania/castelvania3/intro.gif",
        "duration": t2('8.1.1'),
        "timestamp": 138.5,
    })


    # Walker - Front Screen
    walker_data = {
        "deviceid": "front",
        "func": "gsap.start",
        #"source_screen_height": 96,
        "elements": {
            "player": {"src": "castelvania/simon_walk2.gif", "height": "0.5vh", "className": "pixelated"},
            #"medusa": {"src": "castelvania/medusa.gif"     , "height": "0.05vh", "className": "pixelated"}
        },
        "gsap_timeline": [
            ["player"  , "to", "element::player",   0, {"x": "-player.width", "y": "1vh -player.height"}],
            ["player"  , "to", "element::player",  60, {"x": "1vw"}],

            #["medusa_x", "to", "element::medusa",   0, {"x": "1vw"}],
            #["medusa_x", "to", "element::medusa",  60, {"x":     0}],
            #["medusa_y", "to", "element::medusa",   0, {"y": "0.25vh"}],
            #["medusa_y", "to", "element::medusa",   3, {"y": "0.75vh", "ease": "Sine.easeInOut"}],
            #["medusa_y", "yoyo", True],
            #["medusa_y", "repeat", 8]
        ],
        "duration": 60,
        "timestamp": T2_START + (DEFAULT_DURATION * 24),
    }
    el.add_trigger(walker_data)