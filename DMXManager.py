from libs.loop import Loop

from libs.misc import run_func
from libs.network_display_event import DisplayEventHandler as SocketHandler # Name to change! refactor this poo!

from DMXBase import AbstractDMXRenderer, mix
from DMXRendererMidiInput import DMXRendererMidiInput
from DMXRendererLightTiming import DMXRendererLightTiming
from ArtNet3 import ArtNet3

import logging
log = logging.getLogger(__name__)

VERSION = '0.03'

DEFAULT_FRAMERATE = 30
DEFAULT_MIDI_PORT_NAME = 'nanoKONTROL2'
DEFAULT_LIGHTING_SCENES_FOLDER = 'data/scenes'
DEFAULT_LIGHTING_SEQUENCE_FOLDER = 'data/sequences'


class DMXManager(AbstractDMXRenderer):

    def __init__(self, renderers, framerate=DEFAULT_FRAMERATE):
        super().__init__()

        assert len(renderers), "Must provide renderers"
        self.renderers = renderers

        self.artnet = ArtNet3()

        self.net = SocketHandler.factory(recive_func=self.recive)

        self.loop = Loop(framerate)
        self.loop.render = self.render
        self.loop.close = self.close

        self.loop.run()

    def close(self):
        for renderer in self.renderers:
            renderer.close()

    def render(self, frame):
        """
        Frame Event
        Render all registered renderers
        Mix all rendered bytestreams into a single bytestream
        Send DMX display command over network
        """
        mix(self.dmx_universe, *tuple(renderer.render(frame) for renderer in self.renderers))
        self.artnet.dmx(self.dmx_universe.tobytes())

    def recive(self, data):
        """
        Network Event
        Trigger the correct network event to the correct renderer
        """
        run_func(self.renderers, data)


def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description="""DMXManager - Lighting Automation Framework

        """,
        epilog="""
        """
    )
    parser_input = parser

    parser.add_argument('-f', '--framerate', action='store', help='Frames per second to send ArtNet3 packets', default=DEFAULT_FRAMERATE)
    parser.add_argument('--midi_input', action='store', help='name of the midi input port to use', default=DEFAULT_MIDI_PORT_NAME)
    parser.add_argument('--lighting_scenes', action='store', help='folder where the lighting descriptions are to be loaded', default=DEFAULT_LIGHTING_SCENES_FOLDER)
    parser.add_argument('--lighting_sequence', action='store', help='tracks', default=DEFAULT_LIGHTING_SEQUENCE_FOLDER)

    parser.add_argument('--log_level', type=int,  help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=VERSION)

    args = parser.parse_args()

    return vars(args)


if __name__ == "__main__":
    args = get_args()
    logging.basicConfig(level=args['log_level'])

    DMXManager(
        renderers=(
            DMXRendererMidiInput(args['midi_input']),
            DMXRendererLightTiming(args['lighting_scenes'], args['lighting_sequence']),
        ),
        framerate = args['framerate'],
    )
