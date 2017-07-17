import copy
from numbers import Number
from ext.timeline import Timeline


class EventLine():

    def __init__(self, data=None):
        self.tl = Timeline()
        self.events = []  # TODO: Should we rename this to 'triggers'?
        if data:
            for media_event in data:
                self.add_media(media_event)

    def add_media(self, media_event):
        assert issubclass(media_event, dict)
        for required_field in ('deviceid', 'src', 'func', 'timestamp'):
            assert required_field in media_event, f'{required_field} is required for a valid media event'
        if not isinstance(Number, media_event.get('duration')):
            raise NotImplementedError('Extract metadata duration from a remote http src requires implementing. Maybe support range requests from a HTTP wrapper and commit this to hachoir?')
            media_event['duration'] = 0
        self._add_media(media_event)

    def _add_media(self, media_event):
        """
        >>> el = EventLine()
        >>> el._add_media({'deviceid': 'test1', 'duration': 10, 'position': 0, 'timestamp':5})
        >>> el._add_media({'deviceid': 'test2', 'duration': 10, 'position': 0, 'timestamp':10})
        >>> el.get_events_at(0)
        ()
        >>> el.get_events_at(5)
        ({'deviceid': 'test1', 'duration': 10, 'position': 0.0, 'timestamp': 5},)
        >>> el.get_events_at(6)
        ({'deviceid': 'test1', 'duration': 10, 'position': 1.0, 'timestamp': 5},)
        >>> el.get_events_at(10)
        ({'deviceid': 'test1', 'duration': 10, 'position': 5.0, 'timestamp': 5}, {'deviceid': 'test2', 'duration': 10, 'position': 0.0, 'timestamp': 10})
        >>> el.get_events_at(12)
        ({'deviceid': 'test1', 'duration': 10, 'position': 7.0, 'timestamp': 5}, {'deviceid': 'test2', 'duration': 10, 'position': 2.0, 'timestamp': 10})
        >>> el.get_events_at(16)
        ({'deviceid': 'test2', 'duration': 10, 'position': 6.0, 'timestamp': 10},)
        """
        self.events.append(copy.copy(media_event))
        self.tl.from_to(
            media_event,
            media_event['duration'],
            valuesFrom={'position': 0},
            valuesTo={'position': media_event['duration']},
            timestamp=media_event['timestamp']
        )

    @property
    def data(self):
        """
        TODO: return immutable structure
        """
        return self.events

    def get_events_at(self, timecode):
        renderer = self.tl.get_renderer()
        renderer.render(timecode)
        return tuple(i.element for i in renderer._active)

    def render(self, timestamp):
        # TODO: make return immutable
        return self.triggers
