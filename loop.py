import time


class Loop(object):

    def __init__(self, fps):
        self.set_period(fps)

    def set_period(self, fps):
        assert fps, "Provide fps"
        self.period = 1 / fps
        self.previous_frame = 0
        self.start_time = time.time()
        self.previous_time = self.start_time
        return self.period

    @property
    def current_frame(self):
        return int((self.current_time - self.start_time) // self.period)

    def loop(self):
        while self.period:
            self.current_time = time.time()

            for frame_offset in range(self.current_frame - self.previous_frame):
                self.render(self.current_frame + frame_offset)
            self.previous_frame = self.current_frame

            self.pervious_time = self.current_time

            sleep_time = (self.current_time + self.period) - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)

    def render(self, frame):
        print(frame)


def postmortem(func):
    import traceback
    import pdb
    import sys
    try:
        func()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)


if __name__ == "__main__":
    #postmortem(lambda:
            Loop(10).loop()
    #)


