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

    max_frames = 100  #packer.frames  # TODO: Temp test
    bar = progressbar.ProgressBar(
        widgets=(
            'Rendering - Frame: ', progressbar.Counter(),
            ' ', progressbar.Bar(),
            ' ', progressbar.Percentage(),
            ' | ', progressbar.Timer(),
            ' | ', progressbar.ETA(),
            ),
        max_value=max_frames,
    ).start()

    def render(frame):
        bar.update(frame)
        if frame >= max_frames:
            close_event.set()

    loop.render = render
    loop.is_running = lambda: not close_event.is_set()

    log.debug('Enter render loop')
    loop.run()
    log.debug('Exit render loop')

    bar.finish()
    packer.close()
