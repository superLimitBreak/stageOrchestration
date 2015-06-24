import time
import yaml

from libs.misc import file_scan

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererLightTiming(AbstractDMXRenderer):

    DEFAULT_SCENE_NAME = 'none'
    DEFAULT_SEQUENCE_NAME = 'none'
    DEFAULT_BPM = 120.0

    def __init__(self, path_scenes, path_sequences, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scenes = self._open_path(path_scenes, Scene)
        self.sequences = self._open_path(path_sequences, Sequence)

        self.time_start = None
        self.bpm = None

    @staticmethod
    def _open_path(path, target=None):
        """
        Open all yamls in a path by constructing an object for each file based on the 'target' class
        """
        objs = {}
        for file_info in file_scan(path, r'.*\.yaml$'):
            with open(file_info.absolute, 'rb') as file_handle:
                objs[file_info.file_no_ext] = target(yaml.load(file_handle))
        return objs

    def start(self, data):
        self.time_start = time.time()
        self.bpm = float(data.get('bpm', self.DEFAULT_BPM))
        if data.get('sequence'):
            self.sequence = self.sequences[data.get('sequence')]
        if data.get('scene'):
            self.sequence = None #[self.scenes.get(data.get('scene', DEFAULT_SCENE_NAME))]

    def stop(self, data):
        self.time_start = None

    def render(self, frame):
        current_beat = ((time.time() - self.time_start) / 60) * self.bpm
        self.getScene(current_beat)
        return self.dmx_universe

    def get_scene(self, target_beat):
        current_beat = 0
        for scene in self.scenes:
            if target_beat > current_beat and target_beat < current_beat + scene.total_beats:
                return scene
            current_beat += scene.total_beats
        return self.scenes[self.DEFAULT_SCENE_NAME]


class Scene(object):
    def __init__(self, data):
        pass


class Sequence(object):
    def __init__(self, data):
        pass

