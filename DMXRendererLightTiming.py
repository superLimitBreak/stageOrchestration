import time
import yaml

from libs.misc import file_scan

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererLightTiming(AbstractDMXRenderer):

    NULL_SCENE_NAME = 'none'


    def __init__(self, path_scenes, path_tracks, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.scenes = self._open_path(path_scenes)
        self.tracks = self._open_path(path_tracks)

        #print(self.scenes)
        #print('-------------------------------------')
        #print(self.tracks)

        self.time_start = None

    @staticmethod
    def _open_path(path, target=None):
        if not target:
            target = {}
        for file_info in file_scan(path, r'.*\.yaml$'):
            with open(file_info.absolute, 'rb') as f:
                target[file_info.file_no_ext] = yaml.load(f)
        return target


    def start(self, data):
        self.time_start = time.time()
        self.scene = self.scenes[data.get('scene_name', self.NULL_SCENE_NAME)]

    def stop(self, data):
        self.time_start = None

    def render(self, frame):
        current_time = time.time()
        return self.dmx_universe
