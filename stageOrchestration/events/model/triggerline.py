import copy
from numbers import Number
from ext.timeline import Timeline


class TriggerLine():

    def __init__(self, triggers=()):
        self.tl = Timeline()
        self.triggers = []
        self.add_trigger(*triggers)

    def add_trigger(self, *triggers):
        for trigger in triggers:
            #assert issubclass(trigger, dict)
            for required_field in ('deviceid', 'func', 'timestamp'):
                assert required_field in trigger, f'{required_field} is required for a valid media event'
            if not isinstance(trigger.get('duration'), Number):
                raise NotImplementedError('Extract metadata duration from a remote http src requires implementing. Maybe support range requests from a HTTP wrapper and commit this to hachoir?')
                trigger['duration'] = 0
            self._add_trigger(trigger)

    def _add_trigger(self, trigger):
        """
        >>> el = TriggerLine()
        >>> el._add_trigger({'deviceid': 'test1', 'duration': 10, 'position': 0, 'timestamp':5})
        >>> el._add_trigger({'deviceid': 'test2', 'duration': 10, 'position': 0, 'timestamp':10})
        >>> el.get_triggers_at(0)
        ()
        >>> el.get_triggers_at(5)
        ({'deviceid': 'test1', 'duration': 10, 'position': 0.0, 'timestamp': 5},)
        >>> el.get_triggers_at(6)
        ({'deviceid': 'test1', 'duration': 10, 'position': 1.0, 'timestamp': 5},)
        >>> el.get_triggers_at(10)
        ({'deviceid': 'test1', 'duration': 10, 'position': 5.0, 'timestamp': 5}, {'deviceid': 'test2', 'duration': 10, 'position': 0.0, 'timestamp': 10})
        >>> el.get_triggers_at(12)
        ({'deviceid': 'test1', 'duration': 10, 'position': 7.0, 'timestamp': 5}, {'deviceid': 'test2', 'duration': 10, 'position': 2.0, 'timestamp': 10})
        >>> el.get_triggers_at(16)
        ({'deviceid': 'test2', 'duration': 10, 'position': 6.0, 'timestamp': 10},)
        """
        self.triggers.append(copy.copy(trigger))
        self.tl.from_to(
            trigger,
            trigger['duration'],
            valuesFrom={'position': 0},
            valuesTo={'position': trigger['duration']},
            timestamp=trigger['timestamp']
        )

    @property
    def data(self):
        """
        TODO: return immutable structure
        """
        return self.triggers

    def get_triggers_at(self, timecode):
        renderer = self.tl.get_renderer()
        renderer.render(timecode)
        return tuple(i.element for i in renderer._active)

    def render(self, timestamp):
        # TODO: make return immutable
        return self.triggers
