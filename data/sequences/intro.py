import stageOrchestration.lighting.timeline_helpers.colors as color

name = __name__.split('.')[-1]
META = {
    'name': name,
    'bpm': 60,
    'timesignature': '4:4',
}

def create_timeline(dc, t, tl, el):
    tl.set_(dc.get_devices(), color.YELLOW, 0)
    tl.set_(dc.get_devices(), color.YELLOW, 130)

    el.add_trigger({
        "deviceid": "audio",
        "func": "audio.start",
        "src": f"{name}/hibana_intro.ogg",
        "timestamp": t('1.1.1'),
    })


    el.add_trigger({
        "deviceid": "rear",
        "func": "image.show",
        "src": f"logo/superLimitBreak_logo.svg",
        "duration": t('10.1.1'),
        "timestamp": t('2.1.1'),
    })

    RAIN = {
        "func": "particles.start",
        "emitters": {
            "rain": {
                "particleImages": ["assets/HardRain.png"],
                "emitterConfig": {
                    "alpha": {"start": 0.5, "end": 0.5},
                    "scale": {"start": 1, "end": 1},
                    "color": {"start": "ffffff", "end": "ffffff"},
                    "speed": {"start": 2000, "end": 2000},
                    "startRotation": {"min": 80, "max": 80},
                    "rotationSpeed": {"min": 0, "max": 0},
                    "lifetime": {"min": 0.6, "max": 0.6},
                    "blendMode": "normal",
                    "frequency": 0.004,
                    "emitterLifetime": 0,
                    "maxParticles": 1000,
                    "pos": {"x": 0, "y": 0},
                    "addAtBack": False,
                    "spawnType": "rect",
                    "spawnRect": {"x": "-0.5vw", "y": "-0.2vh", "w": "1.5vw", "h": "0.1vh"}
                }
            }
        }
    }

    FIREWORK = {
        "func": "particles.start",
        "emitters": {
            "firework": {
                "particleImages": ["assets/Sparks.png"],
                "emitterConfig": {
                    "alpha": {"start": 1, "end": 0.31},
                    "scale": {"start": 0.5, "end": 1},
                    "color": {"start": "ffffff", "end": "9ff3ff"},
                    "speed": {"start": 100, "end": 100},
                    "acceleration": {"x":0, "y": 200},
                    "startRotation": {"min": 0, "max": 360},
                    "rotationSpeed": {"min": 0, "max": 0},
                    "lifetime": {"min": 1, "max": 3},
                    "blendMode": "normal",
                    "frequency": 0.001,
                    "emitterLifetime": 0.25,
                    "maxParticles": 200,
                    "pos": {"x": "0.5vw", "y": "0.5vh"},
                    "addAtBack": False,
                    "spawnType": "circle",
                    "spawnCircle": {"x": 0, "y": 0, "r": 2}
                }
            }
        }
    }

    el.add_trigger({
        "deviceid": "front",
        "duration": t('10.1.1'),
        "timestamp": t('3.1.1'),
        **RAIN,
    })

    el.add_trigger({
        "deviceid": "front",
        "duration": t('1.1.1'),
        "timestamp": t('4.1.1'),
        **FIREWORK,
    })
