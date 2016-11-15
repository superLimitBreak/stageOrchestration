import logging
from time import sleep

import progressbar

from ext.loop import Loop
from ext.attribute_packer import PersistentFramePacker

from .model.device_collection_loader import device_collection_loader

log = logging.getLogger(__name__)


def render_loop(path_stage_description, path_sequence, framerate, close_event):
    loop = Loop(framerate)
    device_collection = device_collection_loader(path_stage_description)
    packer = PersistentFramePacker(device_collection, path_sequence)

    max_frames = 100  #packer.frames
    bar = progressbar.ProgressBar(
        widgets=(
            'Rendering - Frame: ', progressbar.Counter(),
            ' ', progressbar.Bar(),
            ' ', progressbar.Percentage(),
            ' ', progressbar.Timer(),
            ' ', progressbar.ETA(),
            ),
        max_value=max_frames,
    ).start()

    def render(frame):
        #log.info(f'Render frame {frame}')
        #sleep(0.01)
        bar.update(min(frame, max_frames))
        if frame >= max_frames:
            raise Loop.LoopInterruptException()

    loop.render = render
    loop.running = lambda: not close_event.is_set()

    loop.run()

    log.debug('Exited render loop')
    bar.finish()
    packer.close()
