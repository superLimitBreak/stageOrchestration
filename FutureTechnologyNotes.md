Lighting Future Technologies
============================

`lightingAutomation` will become the system that manages subsiquent triggers.
(This project name could change in the future as it's responsibilitys shift)

Once the Cuebase machine has sent a trigger for 'start the thing' `lightingAutomation` will trigger further subtriggers.
This means the Cuebase machine is not contaminated with having to dealing with things other than music.
with `lightingAutomation` now in control of sub triggers, we can send *eager* triggers with known timecodes to a range of other triggerable devices.

The output of the lighting system will not just be DMX.
We can use it's output to visulise a _mock stage_ to assist with the complexitys of content creation.
This is will be visulised by the `stageViewer` project.


Feature Roadmap
---------------

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
---------------

* Particles on Holographic Screen
    * Devices could be a the main holographic projector with particle effects. Maybe creating particles or flashs timed to the beat.
* Wearable LED's
    * Devices could be wireless performers with rgb led's attached to their cloaths.
    * With network timesyncing it may be possible to use the performers with leds as part of the lighting rig.
    * Think 'Tron' style effects.


High Level Descriptions
-----------------------

Currently lights are described as `performer`_`top/bottom`.
We may perform in a range of differnt enviroments with a range of differnt lights.
It would be good to develop some kind of *higher level abstraction* to describe lights.

If we can describe the stage in general and add additional direction to highlight
performers we could come up with a very flexable general purpuse system that allows us
to create lights for new songs quickly and facilitates us using fourign lighting rigs
with relative ease.

There are lights with moving heads and patern projection.
Different lighting rigs have differnt layouts.
Below are some of the variables we may wish to consider when designing a lighting description system.

* Performer
    * Performers have a rough stage position. With narrow beam lights
* Color
* Motion
    * Some lights can rotate multiple narrow beams. Slow songs may require slow rotation. Some songs may require tween of spinning faster and faster to build tension for a release.
* Focus
    * Lights can be focused into a narrow beam or a wash
* Intensity
    * Slow vocal songs may require intensity on the vocalist. We may want the whole stage to light up as the audience chants the lyrics.
    * Although the colors may be the same for performers, some may have intence moments (drum fills, etc)
* Beat/Pulse
    * (Could overlap with motion?)
    * Could pulse with tween to the heartbeat of a song
* Direction
    * towards audience from behind perofmers (silouet)
    * from above the performer
    * from below the performer
    * from beside the performer
* From/To
    * What if we wanted to describe a sweep of beams across the stage that waved from left to right.
      Maybe finishing pointing at one performer? Maybe sweaping from left to right then when a chorus starts the beams dispurse in random directions.

