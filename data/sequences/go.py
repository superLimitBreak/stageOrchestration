from calaldees.animation.timeline import Timeline

import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *


name = __name__.split('.')[-1]
META = {
    'name': name,
    'bpm': 160,
    'timesignature': '4:4',
}

def create_timeline(dc, t, tl, el):
    tl.set_(dc.get_devices(), color.WHITE, 0)
    tl.set_(dc.get_devices(), color.RED, t('8.1.1'))

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
        "deviceid": "rear",
        "func": "video.start",
        "src": f"{name}/rear.mp4",
        "volume": 0.0,
        "position": 0,
        "timestamp": t('1.1.1') + 0.3,
        "duration": 10,  # FUCKING HACK!!!!
    })


    el.add_trigger({
        "deviceid": "side",
        "func": "text.html_bubble",
        "html": f"""
            <h1>GO!!!</h1>
            <p>Naruto (Opening 4)</p>
            <p>Flow</p>
            <p>Translation: Matt</p>
        """,
        "timestamp": t('2.1.1'),
    })
    el.add_trigger({
        "deviceid": "side",
        "func": "image.start",
        "src": "go/image.png",
        "timestamp": t('2.1.1'),
        "width": "100%",
    })
