Summary
=======

`lightingAutomation` will become the system that manages subsiquent triggers.
(This project name could change in the future as it's responsibilitys shift)

Once the Cuebase machine has sent a trigger for 'start the thing' `lightingAutomation` will trigger further subtriggers.
This means the Cuebase machine is not contaminated with having to dealing with things other than music.
with `lightingAutomation` now in control of sub triggers, we can send *eager* triggers with known timecodes to a range of other triggerable devices.

The output of the lighting system will not just be DMX.
We can use it's output to visulise a _mock stage_ to assist with the complexitys of content creation.
This is will be visulised by the `stageViewer` project.


Feature Roadmap
===============

* Render the entire output to byte arrays in memory on system start
    * Byte arrays directly relate to stage aliased lights
* Create output realtime renderers for
    * DMX
    * JSON (to faciliate `stageViewer`)
* PNG scenes in/out (to faciliate `stageViewer`)
* Scenes can send eager triggers
    * Devices are synced with NTP (If ntp is sufficent)
    * `deviceid: 'main', time:'16:16:03.0451', 'effect.start': 'particles'`
* Sequences/Scenes can have bpms
    * Maybe even bpm tweening


Device Examples
===============

* Particles on Holographic Screen
    * Devices could be a the main holographic projector with particle effects. Maybe creating particles or flashs timed to the beat.
* Wearable LED's
    * Devices could be wireless performers with rgb led's attached to their cloaths.
    * With network timesyncing it may be possible to use the performers with leds as part of the lighting rig.
    * Think 'Tron' style effects.
