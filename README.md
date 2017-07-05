lightingAutomation
==================

superLimitBreak is a band that plays to a click track.
We can trigger stage lights and projections in time to the live music.

`stageOrchestration` can be used standalone but was designed to be paired with
`displayTrigger` which listens to stage events and control digital projectors.


Overview
--------

All the features listed below are goals of the project and are *In development*.

* Input
    * Describe lighting sequences/senes as animation timelines
        * Timing is described in beats/bars and bpm
    * Trigger lighting sequences/scenes with json over TCP
    * Pre recorded sequences can be played (ambilightEncoder)
* Output
    * Control DMX Lights over ArtNet3
    * Preview lighting with stageVisualizer (json/websocket output)
* Web control panel
    * Midi controller sliders can be used for live manipulation of the DMX universe for debugging
    * Lights can be calibrated for stage
        * Dead zones (to keep positional lights away from projectors)
