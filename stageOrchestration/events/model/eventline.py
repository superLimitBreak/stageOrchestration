from ext.timeline import Timeline


class EventLine():

    def __init__(self):
        self.tl = Timeline()

    def add_media(self, media_event, timestamp=None):
        assert issubclass(media_event, dict)
        for required_field in ('deviceid', 'src', 'func'):
            assert required_field in media_event, f'{required_field} is required for a valid media event'
        if 'duration' not in media_event:
            raise NotImplementedError('Extract metadata duration from a remote http src requires implementing. Maybe support range requests from a HTTP wrapper and commit this to hachoir?')
            media_event['duration'] = 0
        self._add_media(media_event, timestamp)

    def _add_media(self, media_event, timestamp=None):
        """
        >>> el = EventLine()
        >>> el._add_media({'deviceid': 'test1', 'duration': 10, 'position': 0}, timestamp=5)
        >>> el._add_media({'deviceid': 'test2', 'duration': 10, 'position': 0}, timestamp=10)
        >>> el.get_events_at(0)
        ()
        >>> el.get_events_at(5)
        ({'deviceid': 'test1', 'duration': 10, 'position': 0.0},)
        >>> el.get_events_at(6)
        ({'deviceid': 'test1', 'duration': 10, 'position': 1.0},)
        >>> el.get_events_at(10)
        ({'deviceid': 'test1', 'duration': 10, 'position': 5.0}, {'deviceid': 'test2', 'duration': 10, 'position': 0.0})
        >>> el.get_events_at(12)
        ({'deviceid': 'test1', 'duration': 10, 'position': 7.0}, {'deviceid': 'test2', 'duration': 10, 'position': 2.0})
        >>> el.get_events_at(16)
        ({'deviceid': 'test2', 'duration': 10, 'position': 6.0},)
        """
        assert 'duration' in media_event
        self.tl.from_to(
            media_event,
            media_event['duration'],
            valuesFrom={'position': 0},
            valuesTo={'position': media_event['duration']},
            timestamp=timestamp
        )

    def get_events_at(self, timecode):
        renderer = self.tl.get_renderer()
        renderer.render(timecode)
        return tuple(i.element for i in renderer._active)

    def render(self, timestamp):
        return tuple()
