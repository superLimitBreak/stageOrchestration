import logging

from ext.loop import Loop

log = logging.getLogger(__name__)

from time import sleep


def render_loop(path_stage_description, path_sequence, framerate, close_event):
    sequence_length = 100  # Temp test
    loop = Loop(framerate)
    packer = PersistentFramePacker(path_sequence)
    def render(frame):
        log.info(f'Render frame {frame}')
        sleep(0.1)
        if frame > sequence_length:
            close_event.set()
    loop.render = render
    loop.running = lambda: not close_event.is_set()
    loop.run()
    packer.close()
