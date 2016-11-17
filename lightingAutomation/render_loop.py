import os.path
import logging
from time import sleep

import progressbar

from ext.loop import Loop
from ext.attribute_packer import PersistentFramePacker

from .model.device_collection_loader import device_collection_loader

log = logging.getLogger(__name__)


def render_loop(path_stage_description, path_sequence, framerate, close_event):
    assert os.path.exists(path_stage_description), f'Unable to render: {path_stage_description} does not exist'
    assert os.path.exists(path_sequence), f'Unable to render: {path_sequence} does not exist'

    loop = Loop(framerate)

    device_collection = device_collection_loader(path_stage_description)
    packer = PersistentFramePacker(device_collection, path_sequence)
    assert packer.frames, 'Nothing to render, packer is empty'

    bar = progressbar.ProgressBar(
        widgets=(
            'Rendering - Frame: ', progressbar.Counter(),
            ' ', progressbar.Bar(),
            ' ', progressbar.Percentage(),
            ' | ', progressbar.Timer(),
            ' | ', progressbar.ETA(),
            ),
        max_value=packer.frames,
    ).start()

    def render(frame):
        packer.restore_frame(frame)

        # TODO: output data_collection to DMX and json

        bar.update(frame)
        if frame >= packer.frames - 1:
            close_event.set()

    loop.render = render
    loop.is_running = lambda: not close_event.is_set()

    log.debug('Enter render loop')
    loop.run()
    log.debug('Exit render loop')

    bar.finish()
    packer.close()
