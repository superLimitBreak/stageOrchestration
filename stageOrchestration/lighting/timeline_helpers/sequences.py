import random
from itertools import cycle

import pytweening

from calaldees.data import get_index_float_blend, set_attr_or_item_all, blend
from calaldees.animation.timeline import Timeline

from . import colors


def hard_cycle(devices, colors, duration):
    """
    Each device cycles though the provided colors in order. No transition or tween.
    """
    assert duration
    assert devices
    assert colors
    tl_intermediate = Timeline()
    for color in colors:
        tl_intermediate.from_to(devices, valuesFrom=color, valuesTo=color, duration=duration)
    return tl_intermediate


def sweep(devices, color, duration, tail=3, color_cleanup=colors.BLACK):
    devices = tuple(devices)
    item_delay = duration / len(devices)
    return (
        Timeline().set_(devices, values=color_cleanup)
        +
        Timeline().staggerTo(devices, item_delay, color, item_delay)
        &
        Timeline().staggerTo(devices[0:-tail], item_delay, color_cleanup, item_delay, timestamp=item_delay * tail)
    )
    #staggerTo(self, elements, duration, values, item_delay, tween=None, timestamp=None):

    # for rgb_strip_lights in (dc.get_device(device_name).lights for device_name in ('floorLarge1', 'floorLarge2')):
    #     tl_intermediate = Timeline()
    #     tl_intermediate.staggerTo(rgb_strip_lights, duration=t('4.1.1'), values={'red': 0, 'green': 1, 'blue': 0}, item_delay=t('1.1.2'))
    #     tl_intermediate.set_(rgb_strip_lights, values={'red': 0, 'green': 0, 'blue': 0})
    #     tl &= tl_intermediate


def pop(devices, duration_attack, duration_decay, valuesTo, tween=pytweening.easeInQuad, tween_out=pytweening.easeOutQuad, valuesFrom=colors.BLACK):
    #tween_out = tween_out or Timeline.Tween.tween_invert(tween)
    return (
        Timeline().from_to(devices, duration_attack, valuesFrom=valuesFrom, valuesTo=valuesTo, tween=tween) # timestamp=-duration_attack
        +
        Timeline().from_to(devices, duration=duration_decay, valuesFrom=valuesTo, valuesTo=valuesFrom, tween=tween_out) # timestamp=0
    )


def light_cycle(devices, states, duration, tween=Timeline.Tween.tween_linear):
    """
    Sweep across the devices with the states (in order)
    """
    devices = tuple(devices)
    states = tuple(states)

    def _render_item_func(pos):
        for device_index, device in enumerate(devices):
            set_attr_or_item_all(
                source=get_index_float_blend(device_index + (pos * len(devices)), states),
                target=device,
            )

    t = Timeline()
    t.animation_item(0, duration, _render_item_func, tween)
    return t


def light_random_frame_fuzz(devices, duration, render_device_func=None, states=None):
    """
    Set each device to a random state from states every single frame render
    """
    assert bool(render_device_func) ^ bool(states)
    if not render_device_func:
        # TODO: assert states is a hard list?
        states = tuple(states)
        render_device_func = lambda: random.choice(states)
    def _render_item_func(pos):
        for device in devices:
            set_attr_or_item_all(source=render_device_func(), target=device)

    t = Timeline()
    t.animation_item(0, duration, _render_item_func)
    return t


def light_random_state(devices, states, durations, max_active_devices=1, randomize_on='devices'):
    assert isinstance(devices, set)
    #if not hasattr(devices, '__iter__'):
    #    devices = (devices, )
    if not hasattr(states, '__iter__'):
        states = (states, )
    if not hasattr(durations, '__iter__'):
        durations = (durations, )
    #if not hasattr(devices, 'index'):
    #    devices = tuple(devices)

    devices_original_states = {device: colors.BLACK for device in devices}  # TODO: implement original state rollback #device.todict()
    _active_devices = set()

    _cycle_iters = {
        'devices': cycle(devices),
        'states': cycle(states),
        #'durations': cycle(durations),
    }
    assert randomize_on in _cycle_iters
    def _get_next(local_variable_name):
        if local_variable_name == randomize_on:
            nonlocal devices
            values = locals()[local_variable_name]
            if randomize_on == 'devices':
                values = tuple(values - _active_devices)
            return random.choice(values)
        return next(_cycle_iters[local_variable_name])

    t = Timeline()
    for duration in durations:
        if len(_active_devices) > max_active_devices:
            _device = _active_devices.pop()
            t.set_(_device, devices_original_states[_device])
        _device, _state = _get_next('devices'), _get_next('states')
        #if not isinstance(_state, dict):
        #    import pdb ; pdb.set_trace()
        assert isinstance(_state, dict)
        t.from_to(_device, duration, valuesFrom=_state, valuesTo=_state)
        _active_devices.add(_device)

    return t
