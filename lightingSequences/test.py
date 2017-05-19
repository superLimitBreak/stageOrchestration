from ext.timeline import Timeline
META = {
    'name': 'Test of tests',
    'bpm': 120,
    'timesigniture': '4:4',
}
def create_timeline(dc, t):
    tl = Timeline()
    #tl.set_(dc.get_device('floorLarge1'), values={'red': 0, 'green': 0, 'blue': 0})
    #tl.from_to(dc.get_devices('sidesFloor'), t('16.0.0'), {'red': 1, 'green':0}, {'red': 0, 'green': 1})
    tl.staggerTo(dc.get_device('floorLarge1').lights, duration=t('8.0.0'), values={'red': 0, 'green': 1}, item_delay=t('1.0.0'))
    return tl
