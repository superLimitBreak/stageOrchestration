from ext.timeline import Timeline

META = {
    'name': 'Test of tests',
    'bpm': 120,
    'timesignature': '4:4',
}

def create_timeline(dc, t, tl, el):
    #tl.set_(dc.get_device('floorLarge1'), values={'red': 0, 'green': 0, 'blue': 0})
    #tl.from_to(dc.get_devices('sidesFloor'), t('16.0.0'), {'red': 1, 'green':0}, {'red': 0, 'green': 1})
    for rgb_strip_lights in (dc.get_device(device_name).lights for device_name in ('floorLarge1', 'floorLarge2')):
        tl_intermediate = Timeline()
        tl_intermediate.staggerTo(rgb_strip_lights, duration=t('4.0.0'), values={'red': 0, 'green': 1, 'blue': 0}, item_delay=t('1.0.0'))
        tl_intermediate.set_(rgb_strip_lights, values={'red': 0, 'green': 0, 'blue': 0})
        tl &= tl_intermediate
    tl = tl * 4

    el.add_trigger({
        "deviceid": "front",
        "func": "video.start",
        "src": "/assets/gurren_lagann.mp4",
        "timestamp": t('0.0.0'),
        "duration": 15,  # TEMP - To be removed with auto duration
    })
    el.add_trigger({
        "deviceid": "rear",
        "func": "video.start",
        "src": "/assets/saikano.mp4",
        "timestamp": t('8.0.0'),
        "duration": 63,  # TEMP - To be removed with auto duration
    })

    return tl