import pytweening

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
