import os.path
import logging
from queue import Full as QueueFullException

import progressbar

from ext.loop import Loop


log = logging.getLogger(__name__)


def frame_count_loop(queue, close_event, frames, frame_rate, title=''):

    bar = progressbar.ProgressBar(
        widgets=(
            f'{title[:8]} - Frame: ', progressbar.Counter(),
            ' ', progressbar.Bar(marker='=', left='[', right=']'),
            ' ', progressbar.Percentage(),
            ' | ', progressbar.Timer(),
            ' | ', progressbar.ETA(),
            ),
        max_value=frames,
    ).start()

    def render(frame):
        try:
            queue.put_nowait(frame)
        except QueueFullException:
            pass

        bar.update(frame)
        if frame >= frames - 1:
            close_event.set()

    loop = Loop(frame_rate)
    loop.render = render
    loop.is_running = lambda: not close_event.is_set()

    log.debug('Enter frame_count_loop')
    loop.run()
    log.debug('Exit frame_count_loop')

    bar.finish()
