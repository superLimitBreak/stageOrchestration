import copy
from numbers import Number
from calaldees.animation.timeline import Timeline


class TriggerLine():

    def __init__(self, triggers=(), get_media_duration_func=None, framerate=None):
        if get_media_duration_func:
            assert callable(get_media_duration_func)
            self.get_media_duration_func = get_media_duration_func
        else:
            def _get_media_duration_func(*args, **kwargs):
                raise Exception('get_media_duration_func is not defined. This is bad? Why has this flow been triggered. Its time to cry.')
            self.get_media_duration_func = _get_media_duration_func
        self.single_frame_duration = (1/framerate) + 0.001 if framerate else 0
        self.tl = Timeline()
        self.triggers = []
        self.add_trigger(*triggers)

    def add_trigger(self, *triggers):
        """
        TODO: test single frame duration
        TODO: test auto image.clear
        """
        for trigger in triggers:
            for required_field in ('func', ):
                assert required_field in trigger, f'{required_field} is required for a valid media event'
            # Auto derive duration of media
            if trigger.get('src') and not isinstance(trigger.get('duration'), Number):
                trigger['duration'] = self.get_media_duration_func(trigger.get('src'))
            # If a framerate is specified, any trigger that has 0 duration is automatically give a duration of 1 frame
            # this ensures that single triggers are activated
            if not trigger.get('duration') and self.single_frame_duration:
                trigger['duration'] = self.single_frame_duration
            assert trigger.get('duration', -1) >= self.single_frame_duration, 'All triggers must have a minimum duration of 1 frame. `add_trigger` has been called without providing timeline with a framerate'
            self._add_trigger(trigger)
            # If Image - Auto add second image.clear trigger after duration
            if trigger.get('func') == 'image.show' and trigger.get('duration'):
                self._add_trigger({
                    'deviceid': trigger.get('deviceid'),
                    'func': 'image.empty',
                    'timestamp': trigger.get('timestamp') + trigger.get('duration') + self.single_frame_duration,
                    'duration': self.single_frame_duration,
                })


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

        >>> el = TriggerLine()
        >>> el._add_trigger({'deviceid': 'test5', 'timestamp': 0, 'func': 'image', 'src': 'file.jpg'})
        >>> el.get_triggers_at(0)
        ({'deviceid': 'test5', 'timestamp': 0, 'func': 'image', 'src': 'file.jpg', 'duration': 0, 'position': 0},)
        >>> el.get_triggers_at(0.1)
        ()

        >>> el = TriggerLine()
        >>> el._add_trigger({'deviceid': 'test6', 'timestamp': 0, 'func': 'image', 'src': 'file.jpg', 'duration': 10})
        >>> el.get_triggers_at(0)
        ({'deviceid': 'test6', 'timestamp': 0, 'func': 'image', 'src': 'file.jpg', 'duration': 10, 'position': 0.0},)
        >>> el.get_triggers_at(5)
        ({'deviceid': 'test6', 'timestamp': 0, 'func': 'image', 'src': 'file.jpg', 'duration': 10, 'position': 5.0},)
        >>> el.get_triggers_at(15)
        ()
        """
        # Validate input ---
        for required_field in ('deviceid', 'timestamp'):
            assert required_field in trigger, f'{required_field} is required for a valid media event'
        # Assert duration is present
        if not isinstance(trigger.setdefault('duration', 0), Number):
            raise AttributeError(f'trigger has no numerical duration {trigger}')
        if not isinstance(trigger.setdefault('position', 0), Number):
            raise AttributeError(f'trigger has no numerical position {trigger}')
        # Auto restrict position to max of duration
        #trigger['position'] = min(trigger['duration'], trigger['position'])

        self.triggers.append(copy.copy(trigger))
        self.tl.from_to(
            trigger,
            max(0, trigger['duration'] - trigger['position']),
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
