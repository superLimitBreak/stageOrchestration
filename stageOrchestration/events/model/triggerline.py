import copy
from numbers import Number
from calaldees.animation.timeline import Timeline


class TriggerLine():

    def __init__(self, triggers=(), get_media_duration_func=None):
        self.get_media_duration_func = get_media_duration_func
        self.tl = Timeline()
        self.triggers = []
        self.add_trigger(*triggers)

    def add_trigger(self, *triggers):
        for trigger in triggers:
            # Auto derive duration of media
            if trigger.get('src') and not trigger.get('duration'):
                trigger['duration'] = self.get_media_duration_func(trigger.get('src'))
            for required_field in ('func', ):
                assert required_field in trigger, f'{required_field} is required for a valid media event'
            self._add_trigger(trigger)

    def _add_trigger(self, trigger):
        """
        >>> el = TriggerLine()
        >>> el._add_trigger({'deviceid': 'test1', 'duration': 10, 'position': 0, 'timestamp':5})
        >>> el._add_trigger({'deviceid': 'test2', 'duration': 10, 'position': 0, 'timestamp':10})
        >>> el._add_trigger({'deviceid': 'test3', 'duration': 10, 'position': 5, 'timestamp':20})
        >>> el._add_trigger({'deviceid': 'test4', 'duration': 0, 'position': 5, 'timestamp':25})
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
        >>> el.get_triggers_at(21)
        ({'deviceid': 'test3', 'duration': 10, 'position': 6.0, 'timestamp': 20},)
        >>> el.get_triggers_at(26)
        ()
        """
        # Validate input ---
        for required_field in ('deviceid', 'timestamp'):
            assert required_field in trigger, f'{required_field} is required for a valid media event'
        # Assert duration is present
        if not isinstance(trigger.get('duration'), Number):
            raise AttributeError(f'trigger has no numerical duration {trigger}')
        if not isinstance(trigger.setdefault('position', 0), Number):
            raise AttributeError(f'trigger has no numerical position {trigger}')
        # Auto restrict position to max of duration
        trigger['position'] = min(trigger['duration'], trigger['position'])

        self.triggers.append(copy.copy(trigger))
        self.tl.from_to(
            trigger,
            trigger['duration'] - trigger['position'],
            valuesFrom={'position': trigger['position']},
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

    def get_render(self):
        return _TriggerRenderWrapper(self.tl.get_renderer())


class _TriggerRenderWrapper():
    def __init__(self, renderer):
        self.renderer = renderer
        self.reset()

    def reset(self):
        self.renderer.reset()
        self.rendered_ids = set()

    def get_triggers_at(self, timecode):
        """
        Will only trigger items once
        """
        self.renderer.render(timecode)
        current_active_item_ids = set(map(id, self.renderer._active))
        new_active_item_ids = current_active_item_ids - self.rendered_ids
        new_active_items = tuple(i.element for i in self.renderer._active if id(i) in new_active_item_ids)
        self.rendered_ids &= current_active_item_ids
        return new_active_items
