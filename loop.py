import time


class Loop(object):

    def __init__(self, fps):
        self.set_period(fps)

    def set_period(self, fps):
        assert fps, "Provide fps"
        self.period = 1 / fps
        self.start_time = time.time()
        self.previous_time = self.start_time
        return self.period

    def get_frame(self, timestamp):
        return int((timestamp - self.start_time) // self.period)

    def loop(self):
        while self.period:
            self.current_time = time.time()

            current_frame = self.get_frame(self.current_time)
            previous_frame = self.get_frame(self.previous_time)
            for frame_offset in range(current_frame - previous_frame):
                self.render(current_frame + frame_offset)

            self.previous_time = self.current_time

            sleep_time = (self.current_time + self.period) - time.time()
            #sleep_time = self.period / 4
            if sleep_time > 0:
                time.sleep(sleep_time)

    def render(self, frame):
        pass
        #print('{0} {1}'.format(frame, time.time()))


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
