stageOrchestration
==================

superLimitBreak is a band that plays to a click track.
We can trigger stage lights and projections in time to the live music.

* `stageOrchestration` can be used standalone but was designed to be paired with
* `displayTrigger` which listens to stage events and control digital projectors
* `stageViewer` can visualize lights/videos in 3d in a webbrowser for development of stage sequences

Overview
--------

All the features listed below are goals of the project and are *in development*.

* Input
  * Describe lighting sequences/senes as animation timelines
    * Timing is described in beats/bars and bpm
  * Trigger lighting sequences/scenes with json over TCP with `displayTrigger`
  * Pre recorded sequences can be played (ambilightEncoder)
* Output
  * Control DMX Lights over ArtNet3
  * Preview lighting with `stageViewer` (json/websocket output)
* Control panel (web interface)
  * Midi controller sliders can be used for live manipulation of the DMX universe for debugging
  * Lights can be calibrated for stage
    * Dead zones (to keep positional lights away from projectors)

Example Use Case Flow
---------------------

* At the start of performing a live track, an audio workstation machine sends a midi note to a virtual midi device
* That virtual midi device is listened to by a web browser running `displayTrigger.triggerWeb`
  * Each note is assigned a different 'start sequence' payload
* A 'start sequence' payload is broadcasts over `displayTrigger.server`
* `stageOrchestration.server` receives the 'start sequence' payload and begins a timer loop to play the requested lighting sequence
* DMX state is broadcast from `stageOrchestration.server` and subsequent video payload triggers are sent to `displayTrigger.server`
  * Subsequent video triggers are rendered by `displayTrigger.display` and seen by the audience
* (A JSON state of the lights can also be broadcast over `displayTrigger.server` and rendered by `stageViewer` to assist content creators visualize the stage)

Setup
-----

```bash
    make install
    make run
```

Reference
---------

[Declarative animations](https://bollu.github.io/mathemagic/declarative/index.html)

### TODO Read
* [Developing a stage lighting system from scratch](https://dl.acm.org/doi/epdf/10.1145/507669.507652)
* [glight](https://github.com/aroffringa/glight)
