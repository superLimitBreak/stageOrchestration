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
        "deviceid": "rear",
        "func": "gsap.start",
        "timestamp": 0.1,
        "duration": 20,
        "elements": {
            "logo": {"src": "logo/superLimitBreak_logo.svg", "height": "1vh", "className": "center"}
        },
    })