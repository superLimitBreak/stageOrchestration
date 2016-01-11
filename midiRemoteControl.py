from libs.pygame_midi_input import MidiInput

import logging
log = logging.getLogger(__name__)

VERSION = '0.01'
DEFAULT_DISPLAYTRIGGER_HOST = '127.0.0.1'


DEVICE_CONFIG = {
    'nanoKONTROL2': dict(
        exit=46,
    ),
}


class MidiRemoteControl(object):
    """
    Send json events over the trigger system to control the lighting
    """

    def __init__(self, midi_device_name):
        super().__init__()

        self.device_config = DEVICE_CONFIG.get(midi_device_name, {})
        assert self.device_config, 'No configuration was found for your midi device. Add device mapping to YAML'

        self.midi_input = MidiInput(midi_device_name)
        self.midi_input.init_pygame()
        self.midi_input.midi_event = self.midi_event  # Dynamic POWER!!!! Remap the midi event to be on this object!

        self.running = True
        while self.running:
            self.midi_input.process_events()  # Poll the midi input per frame (This prevents the need for another thread to monitor the midi state)
        self.close()

    def midi_event(self, event, data1, data2, data3):
        dc = self.device_config
        print(data1, data2, data3)
        if data1 == dc['exit']:
            self.running = False

    def close(self):
        self.midi_input.close()


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""DMXManager - Lighting Automation Framework
        Simple lighting automation for a single DMX universe driven by YAML scene and sequence descriptions.
        """,
        epilog="""
        """
    )
    parser_input = parser

    parser.add_argument('midi_device_name', action='store', help='name of the midi input device to use')

    # Core
    parser.add_argument('--displaytrigger_host', action='store', help='display-trigger server to recieve events from', default=DEFAULT_DISPLAYTRIGGER_HOST)

    # Common
    parser.add_argument('--postmortem', action='store_true', help='enter debugger on exception')
    parser.add_argument('--log_level', type=int,  help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=VERSION)

    args = parser.parse_args()
    return vars(args)


if __name__ == "__main__":
    kwargs = get_args()
    logging.basicConfig(level=kwargs['log_level'])

    def launch():
        MidiRemoteControl(kwargs['midi_device_name'])
    if kwargs.get('postmortem'):
        postmortem(launch)
    else:
        launch()
