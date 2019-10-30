from itertools import cycle, chain

import pytweening

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
    tl.set_(dc.get_devices(), color.YELLOW, 60)

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": f"megalovania/into_with_track.ogg",
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "rear",
        "func": "video.start",
        "src": f"megalovania/intro.mp4",
        "volume": 0.0,
        "timestamp": t('1.1.2'),
    })
