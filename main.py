import random
import array
import time
from threading import Thread
from ola.ClientWrapper import ClientWrapper


class dmx_sender(object):
    def __init__(self, fixture_list):
        self.ola_wrapper = ClientWrapper()
        self.ola_client = self.ola_wrapper.Client()
        self.universe = 0
        self.fixture_list = fixture_list

    # To be used as a sending thread
    def sending_loop(self):
        while True:
            data = array.array('B')

            # for all the fixtures in the fixture_list
            for fix in self.fixture_list:
                # for all the dmx values in the fixture
                for v in fix.get_state():
                    data.append(v)

            # Send the data
            self.send_dmx(data)
            time.sleep(0.1)

    def send_dmx(self, data):
        # send data and lock
        self.ola_client.SendDmx(self.universe, data, self.dmx_unlock)
        self.ola_wrapper.Run()

    def dmx_unlock(self, state):
        # unlock
        self.ola_wrapper.Stop()


class fixture(object):
    def __init__(self):
        self.state = []

    def get_state(self):
        return self.state


class laser(fixture):
    def __init__(self):
        self.state = [150, 60, 84, 253, 0, 0, 255, 133, 0]


class led_wash(fixture):
    def __init__(self):
        self.state = [255, 0, 0, 0, 0, 0, 0, 0]

    def set_random(self):
        self.state = [random.randint(0, 255) for f in range(0, 4)]
        self.state += [0, 0, 0, 0]


las = laser()
l1 = led_wash()
l2 = led_wash()
l3 = led_wash()
l4 = led_wash()


def foo():
    random.seed()
    while True:
        l1.set_random()
        l2.set_random()
        l3.set_random()
        l4.set_random()
        time.sleep(0.1)

t = Thread(target=foo)
t.daemon = True
t.start()

sender = dmx_sender([las, l1, l2, l3, l4])
sender.sending_loop()
