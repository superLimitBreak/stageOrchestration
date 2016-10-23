from functools import wraps

import logging
log = logging.getLogger(__name__)


class Timeline(object):
    """
    Inspired by 'GSAP (GreenSock Animation Platform)' http://greensock.com/
    """
    def __init__(self, delay=0, repeat=0, repeatDelay=0, onUpdate=None, onRepeat=None, onComplete=None):
        pass

    def _invalidate_timeline_cache(self):
        log.debug('TODO: cache cleared')
    def invalidate_timeline_cache(original_function=None):
        """
        Decorator to placeon methods that modify the timeline state
        this invalidates
        """
        def _decorate(function):
            @wraps(function)
            def wrapped_function(self, *args, **kwargs):
                _return = function(self, *args, **kwargs)
                self._invalidate_timeline_cache()
                return _return
            return wrapped_function
        return _decorate(original_function) if original_function else _decorate

    @invalidate_timeline_cache
    def set(self, elements, values):
        return self

    @invalidate_timeline_cache
    def to(self, elements, duration, values, label=None):
        return self

    @invalidate_timeline_cache
    def staggerTo(self, elements, duration, values, offset, label=None):
        return self

    def render(self, timecode):
        pass
