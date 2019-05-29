import logging
import yaml
import os

from config_merger import merge

from calaldees.debug import postmortem, init_vscode_debuger
from calaldees.sigterm import init_sigterm_handler

VERSION = 'v2.0.0dev'

log = logging.getLogger(__name__)


# Constants --------------------------------------------------------------------

DESCRIPTION = """
    lightingAutomation - Stage Orchestration Framework
"""

DEFAULT_CONFIG_FILENAME = 'config.yaml'


# Command Line Arguments -------------------------------------------------------

def get_args():
    import argparse

    parser = argparse.ArgumentParser(
        prog=__name__,
        description=DESCRIPTION,
    )

    parser.add_argument('--config', action='store', help='', default=DEFAULT_CONFIG_FILENAME)
    parser.add_argument('--displaytrigger_host', action='store', help='display-trigger server to recieve events from')

    parser.add_argument('--framerate', action='store', help='Frames per second', type=float)
    parser.add_argument('--dmx_host', action='store', help='ArtNet3 ip address')
    parser.add_argument('--dmx_mapping', action='store', help='map lighting model to dmx address')

    parser.add_argument('--PATH_HOST_media', action='store', help='Path for media - used in local dev for finding duration of media clips for stageViewer')
    parser.add_argument('--path_sequences', action='store', help='Path for lighting sequences')
    parser.add_argument('--path_stage_description', action='store', help='Path for a single stage configuration file')
    parser.add_argument('--scaninterval', action='store', type=float, help='seconds to scan datafiles for changes')

    parser.add_argument('--http_png_port', action='store', help='Port to serve png visulisations for development')

    parser.add_argument('--vscode_debugger', action='store', help='attach to vscode')
    parser.add_argument('--postmortem', action='store', help='Enter debugger on exception')
    parser.add_argument('--log_level', type=int, help='log level')

    parser.add_argument('--version', action='version', version=VERSION)

    kwargs = vars(parser.parse_args())

    return merge(kwargs['config'], os.environ, kwargs, none_values_are_transparent=True)


# Main -------------------------------------------------------------------------

def main(**kwargs):
    from stageOrchestration import server
    server.serve(**kwargs)


if __name__ == "__main__":
    kwargs = get_args()
    logging.basicConfig(level=kwargs['log_level'])
    init_sigterm_handler()

    if kwargs.get('vscode_debugger'):
        init_vscode_debuger()

    def launch():
        main(**kwargs)
    if kwargs.get('postmortem'):
        postmortem(launch)
    else:
        launch()
