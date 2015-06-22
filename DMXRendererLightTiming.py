import yaml

from libs.misc import file_scan

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererLightTiming(AbstractDMXRenderer):

    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scenes = {}
        for file_info in file_scan(path, r'.*\.yaml$'):
            with open(file_info.absolute, 'rb') as f:
                self.scenes[file_info.file_no_ext] = yaml.load(f)
        #print(self.scenes)

    def network_event(self, data):
        print('DMXRendererLightTiming YEE HAW!', data)
