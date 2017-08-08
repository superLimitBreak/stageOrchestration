import os.path
import logging
from queue import Full as QueueFullException

import progressbar

from ext.loop import Loop


log = logging.getLogger(__name__)


def frame_count_loop(queue, close_event, frames, frame_rate, title='', timeshift=0):

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
        if frame >= frames:
            close_event.set()
            return
        try:
            queue.put_nowait(frame)
        except QueueFullException:
            log.warning(f'QueueFullException frame:{frame}')
            pass
        bar.update(frame)

    loop = Loop(frame_rate, timeshift=timeshift)
    loop.render = render
    loop.is_running = lambda: not close_event.is_set()

    log.debug('Enter frame_count_loop')
    loop.run()
    queue.close()
    log.debug('Exit frame_count_loop')

    bar.finish()

