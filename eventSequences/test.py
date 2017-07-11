from stageOrchestration.events.model.eventline import EventLine
META = {
    'name': 'Test of tests',
}
def create_timeline(t):
    el = EventLine()
    el.add_media(
        {
            "deviceid": "front",
            "func": "video.start",
            "src": "/assets/gurren_lagann.mp4",
        },
        t('0.0.0')
    )
    el.add_media(
        {
            "deviceid": "rear",
            "func": "video.start",
            "src": "/assets/saikano.mp4"
        },
        t('4.0.0')
    )
    return el.tl