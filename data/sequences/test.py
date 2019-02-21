from calaldees.animation.timeline import Timeline

META = {
    'name': 'Test of tests',
    'bpm': 138,
    'timesignature': '4:4',
}

def create_timeline(dc, t, tl, el):
    #tl.set_(dc.get_device('floorLarge1'), values={'red': 0, 'green': 0, 'blue': 0})
    #tl.from_to(dc.get_devices('sidesFloor'), t('16.0.0'), {'red': 1, 'green':0}, {'red': 0, 'green': 1})

    #devices = (dc.get_device('floorLarge1'), dc.get_device('floorLarge2'))

    # for rgb_strip_lights in (dc.get_device(device_name).lights for device_name in ('floorLarge1', 'floorLarge2')):
    #     tl_intermediate = Timeline()
    #     tl_intermediate.staggerTo(rgb_strip_lights, duration=t('4.1.1'), values={'red': 0, 'green': 1, 'blue': 0}, item_delay=t('1.1.2'))
    #     tl_intermediate.set_(rgb_strip_lights, values={'red': 0, 'green': 0, 'blue': 0})
    #     tl &= tl_intermediate

    WHITE = {'red': 1, 'green': 1, 'blue': 1}
    BLACK = {'red': 0, 'green': 0, 'blue': 0}
    RED = {'red': 1, 'green': 0, 'blue': 0}
    GREEN = {'red': 0, 'green': 1, 'blue': 0}
    BLUE = {'red': 0, 'green': 0, 'blue': 1}
    YELLOW = {'red': 1, 'green': 1, 'blue': 0}
    CYAN = {'red': 0, 'green': 1, 'blue': 1}
    MAGENTA = {'red': 1, 'green': 0, 'blue': 1}

    def tick_tock(devices, colors, duration=t('1.2.1')):
        tl_intermediate = Timeline()
        for color in colors:
            tl_intermediate.from_to(devices, valuesFrom=color, duration=duration)
        return tl_intermediate

    tl &= tick_tock(dc.get_devices('rear'), (WHITE, BLACK))
    tl &= tick_tock(dc.get_devices('front'), (RED, YELLOW))

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