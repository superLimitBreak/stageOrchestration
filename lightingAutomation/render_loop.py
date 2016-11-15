import logging
from time import sleep

import progressbar

from ext.loop import Loop
from ext.attribute_packer import PersistentFramePacker

from .model.device_collection_loader import device_collection_loader

log = logging.getLogger(__name__)


def render_loop(path_stage_description, path_sequence, framerate, close_event):
    sequence_length = 100  # Temp test
    loop = Loop(framerate)
    device_collection = device_collection_loader(self.path_stage_description)
    packer = PersistentFramePacker(device_collection, path_sequence)

    bar = progressbar.ProgressBar(
        widgets=[progressbar.SimpleProgress()],
        #max_value=packer.frames,
        max_value=sequence_length,
    ).start()

    def render(frame):
        #log.info(f'Render frame {frame}')
        sleep(0.1)
        bar.update(frame)
        if frame > sequence_length:
            close_event.set()

    loop.render = render
    loop.running = lambda: not close_event.is_set()

    loop.run()

    bar.finish()
    packer.close()
