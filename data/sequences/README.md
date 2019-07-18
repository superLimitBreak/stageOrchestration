# sequences

Reference for creating lighting sequences.


## Files
* `__init__.py` must be be present (and empty)
* all `.py` files will be rendered as sequences on system startup
* `.py` files prefixed with `_` will NOT be rendered (these should be used for your own helper functions)


## Imports

* calaldees.animation.timeline
* stageOrchestration.lighting.timeline_functions


## How to `trigger`

JSON Example

```json
    {
        "name": "test-of-tests",
        "events": ["note_on-D1"],
        "payload": [
            {"deviceid": "lights", "func": "lights.start_sequence", "sequence_module_name": "test-of-tests"}
        ]
    }
```

## Examples

```python
    from calaldees.animation.timeline import Timeline
    import stageOrchestration.lighting.timeline_helpers.colors as color
    #from stageOrchestration.lighting.timeline_functions import thing

    META = {
        'name': 'Test of tests',
        'bpm': 120,
        'timesignature': '4:4',
    }

    def create_timeline(dc, t, tl, el):
        tl2 = Timeline()
        tl2.to(dc.get_devices('allLights'), t('4.1.1'), color.RED)
        tl2.to(dc.get_devices('allLights'), t('2.1.1'), color.BLACK)
        tl += tl2

        el.add_trigger({
            "deviceid": "front",
            "func": "video.start",
            "src": "/folder/test.mp4",
            "timestamp": t('1.1.1'),  # Timing is based on beats/bars, 1.1.1 is 0.0
        })
```