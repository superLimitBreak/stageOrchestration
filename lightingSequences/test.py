from ext.timeline import Timeline
META = {
    'name': 'Test of tests',
    'bpm': 120,
    'timesigniture': '4:4',
}
def create_timeline(dc, t):
    tl = Timeline()
    tl.to(dc.get_devices('light1', 'floorLarge1'), t('16.0.0'), {'red': 1})
    return tl
