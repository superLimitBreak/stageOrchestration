from ArtNet3 import ArtNet3
from DMXSimulator import DMXSimulator
from loop import Loop
from pygame_midi_input import MidiInput
import threading

import logging
log = logging.getLogger(__name__)

VERSION = '0.01'


class LightingControl(MidiInput):

    def __init__(self):
        super().__init__('nanoKONTROL2')

    def midi_event(self, event, data1, data2, data3):
        #log.debug(event)
        print('{0} {1} {2} {3}'.format(event, data1, data2, data3))


class LightingAutomation(Loop):

    def __init__(self, framerate=30):
        super().__init__(framerate)
        self.simulator = DMXSimulator(framerate=framerate)
        self.artnet = ArtNet3()
        self.midi_input = LightingControl()

        self.input_thread = threading.Thread(target=self.midi_input.open)
        self.input_thread.daemon = True
        self.input_thread.start()

        self.simulator_thread = threading.Thread(target=self.simulator.start)
        self.simulator_thread.daemon = True
        self.simulator_thread.start()

        self.loop()

    def close(self):
        self.midi_input.running = False
        self.simulator.running = False

    def render(self, frame):
        if frame > 400:
            self.running = False


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""Lighting Automation

        """,
        epilog="""
        """
    )
    parser_input = parser

    parser.add_argument('--log_level', type=int,  help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=VERSION)

    args = parser.parse_args()

    return vars(args)


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    LightingAutomation()
