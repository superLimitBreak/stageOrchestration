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
    T2_START = 62.0
    DEFAULT_DURATION = t2('5.1.1')
    DEFAULT_X_DIFF = 100

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
    }

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


    # Walker - Front Screen
    el.add_trigger({
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
        "timestamp": T2_START + (DEFAULT_DURATION * 8),
    })

    _next = scroll('cmap1', timestamp=T2_START, d=2, x=768, y=4) #x2=2048
    _next = scroll('cmap2', timestamp=_next, x=458, y=4, x_diff=-DEFAULT_X_DIFF)
    _next = scroll('cmap3', timestamp=_next, x=1157, y=67)  # x2=3000
    _next = scroll('cmap4', timestamp=_next, d=0.5, x=6, y=175)  # , x2=1282
    _next = scroll('c3tower', timestamp=_next, d=0.5, x=255, y=2495, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    _next = scroll('c3sunkcity', timestamp=_next, d=0.5, x=3327, y=414, x_diff=-DEFAULT_X_DIFF)
    _next = scroll('cmap5', timestamp=_next, d=0.5, x=750, y=350)
    _next = scroll('cmap6', timestamp=_next, d=2, x=2832, y=368, x_diff=-DEFAULT_X_DIFF)  # , x2=1564

    _next = scroll('c3village', timestamp=_next, d=2, x=0, y=672)
    #scroll('cmap4', timestamp=6, x=1438, y=14)  #, x2=2742
    #scroll('c3clock', timestamp=8, x=256, y=2480, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    #scroll('c3clock', timestamp=9, x=767, y=911, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    #scroll('c3forest', timestamp=10, x=0, y=224)
    #scroll('c3forest', timestamp=11, x=2560, y=415)
    #scroll('c3forest', timestamp=12, x=2304, y=604)
    #scroll('c3sunkcity', timestamp=DEFAULT_DURATION * 9, x=3327, y=414, x_diff=-DEFAULT_X_DIFF)
    #scroll('c3tower', timestamp=DEFAULT_DURATION * 10, x=255, y=2495, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    #scroll('c3tower', timestamp=DEFAULT_DURATION * 11, x=511, y=1583, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    #scroll('c3village', timestamp=DEFAULT_DURATION * 12, x=752, y=672, x_diff=0, y_diff=-DEFAULT_X_DIFF/2)
    #scroll('c3village', timestamp=DEFAULT_DURATION * 13, x=0, y=672)
    #scroll('c3village', timestamp=DEFAULT_DURATION * 14, x=1775, y=192)

    el.add_trigger({
        "deviceid": "front",
        "func": "image.show",
        "src": f"castelvania/castelvania3/intro.gif",
        "duration": t2('8.1.1'),
        "timestamp": 138.5,
    })

