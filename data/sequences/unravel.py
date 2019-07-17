from calaldees.animation.timeline import Timeline

import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *


META = {
    'name': 'unravel',
    'bpm': 120,
    'timesignature': '4:4',
}


def create_timeline(dc, t, tl, el):
    tl.set_(dc.get_devices(), color.RED, 0)
    tl.set_(dc.get_devices(), color.BLACK, t('120.1.1'))

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": "unravel/audio.ogg",
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "front",
        "func": "video.start",
        "src": "unravel/front.mp4",
        "volume": 0.0,
        "position": 0,
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "rear",
        "func": "video.start",
        "src": "unravel/rear.mp4",
        "volume": 0.0,
        "position": 0,
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "side",
        "func": "text.html_bubble",
        "html": """
            <h1>Unravel</h1>
            <p>Tokio Ghul</p>
            <p>(artist)</p>
            <p>Arrangement: Joe</p>
            <p>Translation: Joe</p>
        """,
        "timestamp": t('2.1.1'),
    })
