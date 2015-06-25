import time
import yaml

from libs.misc import file_scan

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererLightTiming(AbstractDMXRenderer):
    """
    Load a dataset of scenes and seqeucnes as dictionarys

    Scene = A lighting scene that has a duration in beats that can render it's state to a dmx_universe
    Sequence = A plain list of scenes to be played in order
    These are loaded from YAML datasets

    start/stop can be triggeded from an external system and reference any of the sequenes or scenes by name

    example start({'sequence':'THE YAML SEQUENCE FILENAME', 'bpm': 120})

    When start is called a start_time is recorded.
    Every time 'render' is called it gets the current time and works out the current 'beat' from the start time
    The correct scene is found in the sequence.
    The scenes 'render' method is called with the current 'beat' into the scene
    """

    DEFAULT_SCENE_NAME = 'none'
    DEFAULT_SEQUENCE_NAME = 'none'
    DEFAULT_BPM = 120.0

    def __init__(self, path_scenes, path_sequences, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scenes = self._open_path(path_scenes, Scene)
        self.sequences = self._open_path(path_sequences)

        self.time_start = 0
        self.bpm = self.DEFAULT_BPM
        self.sequence = ()

    @staticmethod
    def _open_path(path, target_class=None):
        """
        Open all yamls in a path by constructing an object for each file based on the 'target' class
        """
        objs = {}
        for file_info in file_scan(path, r'.*\.yaml$'):
            with open(file_info.absolute, 'rb') as file_handle:
                obj_data = yaml.load(file_handle)
                objs[file_info.file_no_ext] = target_class(obj_data) if target_class else obj_data
        return objs

    def start(self, data):
        """
        Originates from external call from trigger system
        """
        self.time_start = time.time() + data.get('time_offset', 0)
        self.bpm = float(data.get('bpm', self.DEFAULT_BPM))
        if data.get('sequence'):
            self.sequence = self.sequences[data.get('sequence')]
        if data.get('scene'):
            self.sequence = (self.scenes.get(data.get('scene', self.DEFAULT_SCENE_NAME)), )

    def stop(self, data):
        """
        Originates from external call from trigger system
        """
        self.time_start = 0

    @property
    def default_scene(self):
        return self.scenes.get(self.DEFAULT_SCENE_NAME)

    @property
    def default_sequence(self):
        return (self.default_scene, )

    @property
    def current_beat(self):
        return min(0.0, ((time.time() - self.time_start) / 60) * self.bpm if self.time_start else 0.0)

    @property
    def current_sequence(self):
        return (self.scenes.get(scene_name, ) for scene_name in self.sequence) if self.sequence else self.default_sequence

    def render(self, frame):
        scene, scene_beat = self.get_scene_beat(self.current_beat)
        scene.render(self.dmx_universe, scene_beat)
        return self.dmx_universe

    def get_scene_beat(self, target_beat):
        current_beat = 0
        for scene in self.current_sequence:
            if target_beat > current_beat and target_beat < current_beat + scene.total_beats:
                return scene, target_beat - current_beat
            current_beat += scene.total_beats
        return self.default_scene, current_beat - target_beat % self.default_scene.total_beats


class Scene(object):
    def __init__(self, data):
        print("Scene", data)

    @property
    def total_beats(self):
        return 1

    def render(self, dmx_universe, beat):
        pass

