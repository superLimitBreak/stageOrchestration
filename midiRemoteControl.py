import os.path

from libs.misc import postmortem

from libs.pygame_midi_input import MidiInput
from libs.client_reconnect import SubscriptionClient

from lighting import open_yaml

import logging
log = logging.getLogger(__name__)

VERSION = '0.01'
DEFAULT_DISPLAYTRIGGER_HOST = '127.0.0.1'
DEFAULT_YAMLPATH = './data/midiRemoteControlDevices/'


class MidiRemoteControl(object):
    """
    Send json events over the trigger system to control the lighting
    """

    def __init__(self, midi_device_name, displaytrigger_host, yamlpath):
        super().__init__()

        self.device_config = open_yaml(os.path.join(yamlpath, midi_device_name+'.yaml'))
        assert self.device_config, 'No configuration was found for your midi device. Add device mapping to YAML'

        self.parse_config()

        self.midi_input = MidiInput(midi_device_name)
        self.midi_input.init_pygame()
        self.midi_input.midi_event = self.midi_event  # Dynamic POWER!!!! Remap the midi event to be on this object!

        self.socket = SubscriptionClient(*displaytrigger_host.split(':'), subscriptions=('none',))

        self.input_state = {}
        self.raw_index_offset = 0

        # Poll the midi input per frame (This prevents the need for another thread to monitor the midi state)
        self.running = True
        while self.running:
            self.midi_input.process_events()

        self.close()

    def parse_config(self):
        self.input_lookup = {}
        for input_control_config in self.device_config.values():
            if not isinstance(input_control_config, dict):
                continue
            for slider_index in input_control_config.get('sliders', ()):
                self.input_lookup[slider_index] = input_control_config
            if 'input_id' in input_control_config:
                self.input_lookup[input_control_config.get('input_id')] = input_control_config
            #for k, v in value.items():
            #    pass

    def midi_event(self, event, data1, data2, data3):
        self.input_state[data1] = data2/127

        input_config = self.input_lookup.get(data1)
        if not input_config:
            return

        if input_config.get('type') in ('rgb', 'rgbw', 'hsv', ):
            self.send_light_data(
                input_config['device'],
                '{type}:{values}'.format(
                    type=input_config['type'],
                    values=','.join(map(str, (self.input_state.get(slider_index, 0) for slider_index in input_config['sliders'])))
                )
            )
        if input_config.get('type') == 'raw':
            self.send_light_data(
                (self.raw_index_offset * len(input_config['sliders'])) + input_config['sliders'].index(data1),
                self.input_state[data1]
            )

        if input_config.get('command'):
            getattr(self, input_config.get('command'), lambda: None)(self.input_state[data1])

    def send_light_data(self, device, value):
        self.socket.send_message({
            'deviceid': 'lights',
            'func': 'lights.set',
            'device': device,
            'value': value,
        })

    def next_raw(self, value):
        if value:
            self.raw_index_offset += 1
            log.info('Raw input offset {0}'.format(self.raw_index_offset))

    def prev_raw(self, value):
        if value:
            self.raw_index_offset += -1
            log.info('Raw input offset {0}'.format(self.raw_index_offset))

    def smoke(self, value):
        self.send_light_data('smoke', value)

    def all(self, value):
        if value:
            self.send_light_data('all', 'rgb:1,1,1,1')

    def clear(self, value):
        if value:
            self.socket.send_message({'deviceid': 'lights', 'func': 'lights.clear'})

    def all_hold(self, value):
        if value:
            self.all(value)
        else:
            self.clear(127)

    def exit(self, *args):
        self.running = False

    def close(self):
        self.midi_input.close()
        self.socket.close()


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""midiRemoteControl
        Use a midi device input to remotely control a dmx lighting system.
        Send json lighting events using the displaytrigger subscription server.
        """,
        epilog="""
        """
    )
    parser_input = parser

    parser.add_argument('midi_device_name', action='store', help='name of the midi input device to use')

    # Core
    parser.add_argument('--displaytrigger_host', action='store', help='display-trigger server to recieve events from', default=DEFAULT_DISPLAYTRIGGER_HOST)
    parser.add_argument('--yamlpath', action='store', help='folder path for the yaml lighting data.', default=DEFAULT_YAMLPATH)

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
        MidiRemoteControl(kwargs['midi_device_name'], kwargs['displaytrigger_host'], kwargs['yamlpath'])
    if kwargs.get('postmortem'):
        postmortem(launch)
    else:
        launch()
