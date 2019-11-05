from calaldees.animation.timeline import Timeline

import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *


name = __name__.split('.')[-1]
META = {
    'name': name,
    'bpm': 140,
    'timesignature': '4:4',
}


def create_timeline(dc, t, tl, el):
    tl.set_(dc.get_devices(), color.GREEN, 0)
    tl.set_(dc.get_devices(), color.BLACK, t('4.1.1'))


    # el.add_trigger({
    #     "deviceid": "audio",
    #     "func": "audio.start",
    #     "src": f"{name}/audio.ogg",
    #     "timestamp": t('1.1.1'),
    # })
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
        "html": """
            <h1>Again</h1>
            <p>Full Metal Alchemist Brotherhood</p>
            <p>(artist)</p>
            <p>Arrangement: Joe</p>
            <p>Translation: superLimitBreak</p>
        """,
        "timestamp": t('2.1.1'),
    })
    el.add_trigger({
        "deviceid": "side",
        "func": "image.start",
        "src": "again/image.png",
        "timestamp": t('2.1.1'),
        "width": "100%",
    })
