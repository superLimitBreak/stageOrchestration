import random
from itertools import cycle

from pytweening import easeInOutQuint

from calaldees.animation.timeline import Timeline

import stageOrchestration.lighting.timeline_helpers.colors as color
from stageOrchestration.lighting.timeline_helpers.sequences import *

META = {
    'name': 'Test of tests',
    'bpm': 138,
    'timesignature': '4:4',
}


from calaldees.data import get_index_float_blend, set_attr_or_item_all, blend


def light_cycle(devices, colors, duration, tween=Timeline.Tween.tween_linear):
    colors = tuple(colors)

    def render_item_func(pos):
        for device_index, device in enumerate(devices):
            set_attr_or_item_all(
                source=get_index_float_blend(device_index + (pos * len(devices)), colors),
                target=device,
            )

    t = Timeline()
    t.animation_item(0, duration, render_item_func, tween)
    return t


def light_random_state(devices, states, durations, max_active_devices=1, randomize_on='devices'):
    if not hasattr(states, '__iter__'):
        states = (states, )
    if not hasattr(durations, '__iter__'):
        durations = (durations, )

    devices_original_states = {device: device.todict() for device in devices}
    _active_devices = set()

    _cycle_iters = {
        'devices': cycle(devices),
        'states': cycle(states),
        #'durations': cycle(durations),
    }
    assert randomize_on in _cycle_iters
    def _get_next(local_variable_name):
        if local_variable_name == randomize_on:
            values = locals()[local_variable_name]
            if randomize_on == 'devices':
                values = set(values) - _active_devices
            return random.choice(values)
        return next(_cycle_iters[local_variable_name])

    t = Timeline()
    for duration in durations:
        if len(_active_devices) > max_active_devices:
            _device = _active_devices.pop()
            t.set_(_device, devices_original_states[_device])
        _device, _state = _get_next('devices'), _get_next('states')
        t.from_to(_device, duration, valuesFrom=_state, valuesTo=_state)
        _active_devices.add(_device)

    return t



def create_timeline(dc, t, tl, el):
    #tl.set_(dc.get_device('floorLarge1'), values={'red': 0, 'green': 0, 'blue': 0})
    #tl.from_to(dc.get_devices('sidesFloor'), t('16.0.0'), {'red': 1, 'green':0}, {'red': 0, 'green': 1})

    #devices = (dc.get_device('floorLarge1'), dc.get_device('floorLarge2'))

    rythm = (t('1.2.1'),) * 3 + (t('1.1.2'),) * 4 + (t('1.2.1'),) * 3 + (t('1.1.2'),) * 8


    tl &= pop(dc.get_devices('rear'), duration_attack=t('1.1.2'), duration_decay=t('1.1.4'), valuesTo=color.WHITE, tween=None, tween_out=None) * 2
    tl &= hard_cycle(dc.get_devices('front') - {dc.get_device('floorFrontBarCenter'),}, (color.RED, color.YELLOW), t('1.2.1'))
    #tl += sweep(dc.get_device('floorFrontBarCenter').lights, color.RED, t('1.2.1')) + sweep(reversed(dc.get_device('floorFrontBarCenter').lights), color.RED, t('1.2.1'))
    RED_DARK = blend(color.BLACK, color.RED, blend=0.6)
    colors = (RED_DARK, color.RED, RED_DARK) + ((color.BLACK,) * 5)
    tl &= (
        light_cycle(dc.get_device('floorFrontBarCenter').lights, colors=colors, duration=t('1.2.1'), tween=easeInOutQuint)
        +
        light_cycle(dc.get_device('floorFrontBarCenter').lights, colors=colors, duration=t('1.2.1'), tween=Timeline.Tween.tween_invert(easeInOutQuint))
    )

    tl = tl * 24

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": "bad-apple/badApple_withClick.ogg",
        "timestamp": t('1.1.1'),
    })
    el.add_trigger({
        "deviceid": "rear",
        "func": "video.start",
        "src": "bad-apple/bad-apple_original.mp4",
        "volume": 0.0,
        "position": 1.3,
        "timestamp": t('1.1.1'),
    })

    return tl