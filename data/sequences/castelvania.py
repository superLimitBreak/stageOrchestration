from functools import partial

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
    tl.set_(dc.get_devices(), color.YELLOW, t('123.1.1'))

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
        "deviceid": "rear",
        "func": "image.start",
        "src": "castelvania/castelvania1/cmap1.png",
        "width": 3600,
        "height": 350,
        "source_screen_height": 168,
        "className": "pixelated",
        "gsap_animation": [
            ["to",  0, {"x":     0, "y": -18, "ease":"linear", "force3D": False}],
            ["to", 58, {"x":  -560          , "ease":"linear"}]
        ],
        "timestamp": 1,
    })
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


    # Background Scroll --------------------------------------------------------

    t2 = partial(timecode_to_seconds, bpm=232)
    DEFAULT_DURATION = t2('5.1.1')
    DEFAULT_X_DIFF = 1400

    IMAGES = {
        'cmap1': {"src": "castelvania/castelvania1/cmap1.png", "width": 3600, "height": 350},
        'cmap3': {"src": "castelvania/castelvania1/cmap3.png", "width": 3600, "height": 600},
        'cmap4': {"src": "castelvania/castelvania1/cmap4.png", "width": 4000, "height": 400},
        'cmap6': {"src": "castelvania/castelvania1/cmap6.png", "width": 3100, "height": 550},
        'c3clock': {"src": "castelvania/castelvania3/clocktowerofuntimelydeath.png", "width": 1024, "height": 2688},
        'c3forest': {"src": "castelvania/castelvania3/madforest.png", "width": 3584, "height": 992},
        'c3sunkcity': {"src": "castelvania/castelvania3/sunkencityofpoltergeist.png", "width": 3584, "height": 800},
        'c3tower': {"src": "castelvania/castelvania3/towerofterror.png", "width": 768, "height": 2688},
        'c3village': {"src": "castelvania/castelvania3/warakiyavillage.png", "width": 4096, "height": 864},
    }

    def scroll(image_name, timestamp=0, duration=DEFAULT_DURATION, x=0, y=0, x_diff=DEFAULT_X_DIFF, y_diff=0, _timestamp_base=62.0):
        trigger = {
            "deviceid": "rear",
            "func": "image.start",
            "source_screen_height": 168,
            "className": "pixelated",
            "gsap_animation": [
                ["to", 0, {"x": -x, "y": -y, "ease":"linear", "force3D": False}],
                ["to", duration, {
                    "x": -x -x_diff if x_diff else -x,
                    "y": -y -y_diff if y_diff else -y,
                    "ease":"linear",
                }]
            ],
            "timestamp": _timestamp_base + timestamp,
        }
        trigger.update(IMAGES[image_name])
        el.add_trigger(trigger)

    scroll('cmap1', timestamp=0, x=768, y=4) #x2=2048
    scroll('cmap3', timestamp=DEFAULT_DURATION * 1, x=1157, y=67)  # x2=3000
    scroll('cmap4', timestamp=DEFAULT_DURATION * 2, x=6, y=175)  # , x2=1282
    scroll('cmap4', timestamp=DEFAULT_DURATION * 3, x=1438, y=14)  #, x2=2742
    scroll('cmap6', timestamp=DEFAULT_DURATION * 4, x=2832, y=368, x_diff=-DEFAULT_X_DIFF)  # , x2=1564
    scroll('c3clock', timestamp=DEFAULT_DURATION * 5, x=256, y=2480, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    scroll('c3clock', timestamp=DEFAULT_DURATION * 6, x=767, y=911, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    scroll('c3forest', timestamp=DEFAULT_DURATION * 7, x=0, y=224)
    scroll('c3forest', timestamp=DEFAULT_DURATION * 7, x=2560, y=415)
    scroll('c3forest', timestamp=DEFAULT_DURATION * 7, x=2304, y=604)
    scroll('c3sunkcity', timestamp=DEFAULT_DURATION * 8, x=3327, y=414, x_diff=-DEFAULT_X_DIFF)
    scroll('c3sunkcity', timestamp=DEFAULT_DURATION * 9, x=3327, y=414, x_diff=-DEFAULT_X_DIFF)
    scroll('c3tower', timestamp=DEFAULT_DURATION * 10, x=255, y=2495, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    scroll('c3tower', timestamp=DEFAULT_DURATION * 11, x=511, y=1583, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    scroll('c3village', timestamp=DEFAULT_DURATION * 12, x=752, y=672, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    scroll('c3village', timestamp=DEFAULT_DURATION * 13, x=0, y=672)
    scroll('c3village', timestamp=DEFAULT_DURATION * 14, x=1775, y=192)


    # Notes --------------------------------------------------------------------

    gasp_test = {
        "deviceid": "front",
        "func": "gsap.start",
        "source_screen_height": 168,
        "elements": {
            "player": {"src": "castelvania/simon_walk2.gif", "height": "0.25vh", "className": "pixelated"},
            "medusa": {"src": "castelvania/medusa.gif"     , "height": "0.05vh", "className": "pixelated"}
        },
        "gsap_timeline": [
            ["player"  , "to", "element::player",   0, {"x": 0                  , "y": "1vh -player.height"}],
            ["player"  , "to", "element::player",  60, {"x": "1vw -player.width"                           }],

            ["medusa_x", "to", "element::medusa",   0, {"x": "1vw"}],
            ["medusa_x", "to", "element::medusa",  60, {"x":     0}],
            ["medusa_y", "to", "element::medusa",   0, {"y": "0.25vh"}],
            ["medusa_y", "to", "element::medusa",   3, {"y": "0.75vh", "ease": "Sine.easeInOut"}],
            ["medusa_y", "yoyo", True],
            ["medusa_y", "repeat", 8]
        ],
        "duration": 60,
        "timestamp": t('2.1.1'),
    } # el.add_trigger(
