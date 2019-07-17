from calaldees.animation.timeline import Timeline

import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *


META = {
    'name': 'outlaw-star',
    'bpm': 108,
    'timesignature': '4:4',
}


def create_timeline(dc, t, tl, el):
    tl.set_(dc.get_devices(), color.CYAN, 0)
    tl.set_(dc.get_devices(), color.RED, t('123.1.1'))

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": "outlaw-star/audio.ogg",
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "front",
        "func": "video.start",
        "src": "outlaw-star/front.mp4",
        "volume": 0.0,
        "position": 0,
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "rear",
        "func": "video.start",
        "src": "outlaw-star/rear.mp4",
        "volume": 0.0,
        "position": 0,
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "side",
        "func": "text.html_bubble",
        "html": """
            <h1>(title)</h1>
            <p>Outlaw Star</p>
            <p>(artist)</p>
            <p>Arrangement: Joe</p>
            <p>Translation: superLimitBreak</p>
        """,
        "timestamp": t('2.1.1'),
    })
