import os.path
import logging

import progressbar

from ext.loop import Loop


log = logging.getLogger(__name__)


class FrameReader():

    def __init__(self, path_sequence, frame_size):
        assert os.path.exists(path_sequence), f'Unable to render: {path_sequence} does not exist'
        filesize = os.stat(path_sequence).st_size
        assert filesize, f'Nothing to render, {path_sequence} is empty'
        self.frame_size = frame_size
        self.frames = filesize / frame_size
        self.sequence_filehandle = open(path_sequence, 'rb')

    def read_frame(self, frame):
        assert frame >= 0 and frame < self.frames, f'frame {frame} out of range 0 to {self.frames}'
        self.sequence_filehandle.seek(frame * self.frame_size)
        return self.sequence_filehandle.read(self.frame_size)

    def close(self):
        self.sequence_filehandle.close()
        self.sequence_filehandle = None
