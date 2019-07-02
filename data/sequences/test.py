import random
from itertools import cycle, chain

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

    devices_original_states = {device: color.BLACK for device in devices}  # TODO: implement original state rollback #device.todict()
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



def create_timeline(dc, t, tl, el):
    #tl.set_(dc.get_device('floorLarge1'), values={'red': 0, 'green': 0, 'blue': 0})
    #tl.from_to(dc.get_devices('sidesFloor'), t('16.0.0'), {'red': 1, 'green':0}, {'red': 0, 'green': 1})

    #devices = (dc.get_device('floorLarge1'), dc.get_device('floorLarge2'))

    rhythm = (t('1.2.1'),) * 3 + (t('1.1.2'),) * 4 + (t('1.2.1'),) * 3 + (t('1.1.3'),) * 2


    #tl += sweep(dc.get_device('floorFrontBarCenter').lights, color.RED, t('1.2.1')) + sweep(reversed(dc.get_device('floorFrontBarCenter').lights), color.RED, t('1.2.1'))

    # Intro 1 ------------------------------------------------------------------
    tl_intro_1 = Timeline()
    for x in range(4):
        tl_intro_1 += light_random_state(dc.get_devices('allLights'), (color.WHITE, ), rhythm)

    # Intro 2 ------------------------------------------------------------------
    tl_intro_2 = Timeline()

    tl_intro_2 &= pop(
        dc.get_devices('rear'),
        duration_attack=t('1.1.2'),
        duration_decay=t('1.1.4'),
        valuesTo=color.WHITE,
        tween=None,
        tween_out=None
    ) * 2

    tl_intro_2 &= hard_cycle(
        dc.get_devices('front') - {dc.get_device('floorFrontBarCenter'),},
        (color.RED, color.YELLOW),
        t('1.2.1'),
    )

    RED_DARK = blend(color.BLACK, color.RED, blend=0.6)
    colors = (RED_DARK, color.RED, RED_DARK) + ((color.BLACK,) * 5)
    tl_intro_2 &= (
        light_cycle(dc.get_device('floorFrontBarCenter').lights, states=colors, duration=t('1.2.1'), tween=easeInOutQuint)
        +
        light_cycle(dc.get_device('floorFrontBarCenter').lights, states=colors, duration=t('1.2.1'), tween=Timeline.Tween.tween_invert(easeInOutQuint))
    )

    tl_intro_2 = tl_intro_2 * 16

    # Fuzz ---------------------------------------------------------------------
    tl_fuzz = light_random_frame_fuzz(
        devices=tuple(chain.from_iterable(strip_light.lights for strip_light in dc.get_devices('floorFrontBarLeft', 'floorFrontBarCenter', 'floorFrontBarRight'))),
        duration=t('3.1.1'),
        states=(
            color.CYAN, color.BLUE, color.MAGENTA, color.WHITE, color.YELLOW,
        )
    )

    # Main ---------------------------------------------------------------------
    tl = (
        tl_intro_1 +
        tl_intro_2 +
        tl_fuzz
    )

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