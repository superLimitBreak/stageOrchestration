import os.path
import logging
from queue import Full as QueueFullException

import progressbar

from ext.loop import Loop


log = logging.getLogger(__name__)


def timer_loop(path_sequence, frame_size, frame_rate, close_event, data_queue):
    assert os.path.exists(path_sequence), f'Unable to render: {path_sequence} does not exist'
    filesize = os.stat(path_sequence).st_size
    assert filesize, f'Nothing to render, {path_sequence} is empty'
    frames = filesize / frame_size
    sequence_filehandle = open(path_sequence, 'rb')

    bar = progressbar.ProgressBar(
        widgets=(
            'Rendering - Frame: ', progressbar.Counter(),
            ' ', progressbar.Bar(marker='=', left='[', right=']'),
            ' ', progressbar.Percentage(),
            ' | ', progressbar.Timer(),
            ' | ', progressbar.ETA(),
            ),
        max_value=frames,
    ).start()

    def render(frame):
        sequence_filehandle.seek(frame * frame_size)
        try:
            data_queue.put_nowait(sequence_filehandle.read(frame_size))
        except QueueFullException:
            pass

        bar.update(frame)
        if frame >= frames - 1:
            close_event.set()

    loop = Loop(frame_rate)
    loop.render = render
    loop.is_running = lambda: not close_event.is_set()

    log.debug('Enter render_loop')
    loop.run()
    log.debug('Exit render_loop')

    bar.finish()
    sequence_filehandle.close()
