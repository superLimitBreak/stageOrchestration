# sequences

Reference for creating lighting sequences.


## Files
* `__init__.py` must be be present (and empty)
* all `.py` files will be rendered as sequences
* `.py` files prefixed with `_` will NOT be rendered (these should be used for your own helper functions)


## Imports

* calaldees.animation.timeline
* stageOrchestration.lighting.timeline_functions


## How to `trigger`

JSON Example

```json
    {

    }
```

## Examples

```python
    from calaldees.animation.timeline import Timeline
    #from stageOrchestration.lighting.timeline_functions import thing

    META = {
        'name': 'Test of tests',
        'bpm': 120,
        'timesignature': '4:4',
    }

    def create_timeline(dc, t, tl, el):
        tl2 = tl_intermediate = Timeline()
        tl = tl + tl2

        el.add_trigger({
            "deviceid": "front",
            "func": "video.start",
            "src": "/folder/test.mp4",
            "duration": 15,  # TEMP - To be removed with auto duration
            "timestamp": t('0.0.0'),
        })

        return tl
```