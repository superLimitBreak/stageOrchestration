from calaldees.animation.timeline import Timeline
import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *

META = {
    'name': 'Test of tests',
    'bpm': 138,
    'timesignature': '4:4',
}


def create_timeline(dc, t, tl, el):
    #tl.set_(dc.get_device('floorLarge1'), values={'red': 0, 'green': 0, 'blue': 0})
    #tl.from_to(dc.get_devices('sidesFloor'), t('16.0.0'), {'red': 1, 'green':0}, {'red': 0, 'green': 1})

    #devices = (dc.get_device('floorLarge1'), dc.get_device('floorLarge2'))

    tl &= pop(dc.get_devices('rear'), color.WHITE, t('1.2.1'))
    tl &= hard_cycle(dc.get_devices('front') - {dc.get_device('floorFrontBarCenter'),}, (color.RED, color.YELLOW), t('1.2.1'))
    tl &= sweep(dc.get_device('floorFrontBarCenter').lights, color.RED, t('1.2.1')) + sweep(reversed(dc.get_device('floorFrontBarCenter').lights), color.RED, t('1.2.1'))

    tl = tl * 128

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": "bad-apple/badApple_withClick.ogg",
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "rear",
        "func": "video.start",
        "src": "bad-apple/bad-apple_original.mp4",
        "volume": 0.0,
        "position": 1.3,
        "timestamp": t('1.1.1'),
    })

    return tl