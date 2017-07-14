from stageOrchestration.events.model.eventline import EventLine


def eventline_loader(filepath):
    """
    """
    el = EventLine()
    return el

def create_timeline(t):

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