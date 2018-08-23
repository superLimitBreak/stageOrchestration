import os.path
import logging
from multiprocessing import Event as MultiprocessingEvent
from queue import Full as QueueFullException

import progressbar

from calaldees.loop import Loop
from calaldees.timecode import nearest_timecode_to_next_frame


log = logging.getLogger(__name__)

FRAME_NUMBER_COMPLETE = -1


def frame_count_loop(queue, close_event, frames, frame_rate, title='', timecode=0):
    timecode = nearest_timecode_to_next_frame(timecode, frame_rate)

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

    natural_finish_event = MultiprocessingEvent()

    def render(frame):
        if frame >= frames:
            natural_finish_event.set()
            close_event.set()
            return
        try:
            queue.put_nowait(frame)
        except QueueFullException:
            log.warning(f'QueueFullException frame:{frame}')
            pass
        bar.update(frame)

    loop = Loop(frame_rate, timeshift=timecode)
    loop.render = render
    loop.is_running = lambda: not close_event.is_set()

    log.debug('Enter frame_count_loop')
    loop.run()
    if natural_finish_event.is_set():
        queue.put_nowait(FRAME_NUMBER_COMPLETE)
    queue.close()
    log.debug('Exit frame_count_loop')

    bar.finish()
