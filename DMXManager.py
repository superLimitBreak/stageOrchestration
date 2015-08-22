from libs.loop import Loop

from libs.misc import run_funcs, postmortem
from libs.network_display_event import DisplayEventHandler as SocketHandler # Name to change! refactor this poo!

from DMXBase import AbstractDMXRenderer, mix

from ArtNet3 import ArtNet3

import logging
log = logging.getLogger(__name__)

VERSION = '0.04'

DEFAULT_DISPLAYTRIGGER_HOST = '127.0.0.1'
DEFAULT_ARTNET_DMX_HOST = '127.0.0.1'
DEFAULT_FRAMERATE = 30
DEFAULT_YAMLPATH = 'data'
DEFAULT_YAML_SCAN_INTERVAL = 1.0

class DMXManager(AbstractDMXRenderer):

    def __init__(self, renderers, **kwargs):
        """
        """
        super().__init__()

        assert len(renderers), "Must provide renderers"
        self.renderers = renderers

        self.artnet = ArtNet3(host=kwargs['artnet_dmx_host'])

        if kwargs.get('displaytrigger_host'):
            self.net = SocketHandler.factory(host=kwargs['displaytrigger_host'], recive_func=self.recive)

        self.loop = Loop(kwargs['framerate'])
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
        mix(self.dmx_universe, tuple(renderer.render(frame) for renderer in self.renderers))
        self.artnet.dmx(self.dmx_universe.tobytes())

    def recive(self, data):
        """
        Network Event
        Trigger the correct network event to the correct renderer
        """
        run_funcs(data, self.renderers)


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

    # Core
    parser.add_argument('--displaytrigger_host', action='store', help='display-trigger server to recieve events from', default=DEFAULT_DISPLAYTRIGGER_HOST)
    parser.add_argument('-f', '--framerate', action='store', help='Frames per second to send ArtNet3 packets', default=DEFAULT_FRAMERATE)
    parser.add_argument('--artnet_dmx_host', action='store', help='ArtNet3 ip address', default=DEFAULT_ARTNET_DMX_HOST)

    # Plugin params
    parser.add_argument('--midi_input', action='store', help='name of the midi input port to use')
    parser.add_argument('--yamlpath', action='store', help='folder path for the yaml lighting data.', default=DEFAULT_YAMLPATH)
    parser.add_argument('--yamlscaninterval', action='store', type=float, help='seconds to scan', default=DEFAULT_YAML_SCAN_INTERVAL)

    # Common
    parser.add_argument('--log_level', type=int,  help='log level', default=logging.INFO)
    parser.add_argument('--version', action='version', version=VERSION)

    args = parser.parse_args()
    return vars(args)


def main():
    kwargs = get_args()
    logging.basicConfig(level=kwargs['log_level'])

    renderers = []
    if kwargs.get('midi_input'):
        from DMXRendererMidiInput import DMXRendererMidiInput
        renderers.append(DMXRendererMidiInput(kwargs['midi_input']))
        log.info('DMXRendererMidiInput')
    if kwargs.get('yamlpath'):
        from DMXRendererLightTiming import DMXRendererLightTiming
        from DMXRendererDisplayTriggerEvents import DMXRendererDisplayTriggerEvents
        dmx_lighting_renderer = DMXRendererLightTiming(kwargs['yamlpath'], rescan_interval=kwargs['yamlscaninterval'])
        renderers.append(dmx_lighting_renderer)
        renderers.append(DMXRendererDisplayTriggerEvents(dmx_lighting_renderer))
        log.info('DMXRendererLightTiming')
    try:
        from DMXRendererPentatonicHero import DMXRendererPentatonicHero
        renderers.append(DMXRendererPentatonicHero())
        log.info('DMXRendererPentatonicHero')
    except ImportError:
        pass

    DMXManager(renderers, **kwargs)


if __name__ == "__main__":
    postmortem(main)

