from calaldees.animation.timeline import Timeline

import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *


name = __name__.split('.')[-1]
META = {
    'name': name,
    'bpm': 120,
    'timesignature': '4:4',
}

def create_timeline(dc, t, tl, el):
    tl.set_(dc.get_devices(), color.YELLOW, 0)
    tl.set_(dc.get_devices(), color.YELLOW, t('123.1.1'))

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": f"{name}/audio.ogg",
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
    # el.add_trigger({
    #     "deviceid": "rear",
    #     "func": "video.start",
    #     "src": f"{name}/rear.mp4",
    #     "volume": 0.0,
    #     "position": 0,
    #     "timestamp": t('1.1.1'),
    # })
    el.add_trigger({
        "deviceid": "side",
        "func": "text.html_bubble",
        "html": f"""
            <h1>(title)</h1>
            <p>{name}</p>
            <p>(artist)</p>
            <p>Arrangement: Joe</p>
        """,
        "timestamp": t('2.1.1'),
    })
    el.add_trigger({
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
    })
