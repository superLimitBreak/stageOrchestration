import logging
import multiprocessing
import importlib
import os.path
import re

from ext.client_reconnect import SubscriptionClient
from ext.misc import file_scan_diff_thread, multiprocessing_process_event_queue, fast_scan, fast_scan_regex_filter
from ext.loop import Loop

log = logging.getLogger(__name__)

REGEX_PY_EXTENSION = re.compile(r'\.py$')
FAST_SCAN_REGEX_FILTER_FOR_PY_FILES = fast_scan_regex_filter(file_regex=REGEX_PY_EXTENSION, ignore_regex=r'^_')

def serve(**kwargs):
    log.info('Serve {}'.format(kwargs))
    server = LightingServer(**kwargs)
    server.run()


class LightingServer(object):

    def __init__(self, **kwargs):
        self.framerate = kwargs['framerate']

        self.network_event_queue = multiprocessing.Queue()
        if kwargs.get('displaytrigger_host'):
            self.net = SubscriptionClient(host=kwargs['displaytrigger_host'], subscriptions=('lights', 'all'))
            self.net.recive_message = lambda msg: self.network_event_queue.put(msg)

        self.scan_update_event_queue = multiprocessing.Queue()
        if 'scaninterval' in kwargs:
            self.scan_update_event_queue = file_scan_diff_thread(
                self.path_sequences,
                search_filter=FAST_SCAN_REGEX_FILTER_FOR_PY_FILES,
                rescan_interval=kwargs['scaninterval']
            )

        self.path_sequences = kwargs['path_sequences']
        self.sequences = {}
        self.reload_sequences()


    # Event Handling -------------------------------------------------------

    def run(self):
        multiprocessing_process_event_queue({
            self.network_event_queue: self.network_event,
            self.scan_update_event_queue: self.scan_update_event,
        })

    def network_event(self, event):
        log.info(event)

    def scan_update_event(self, sequence_files):
        self.reload_sequences(sequence_files)

    # Sequences -------------------------------------------------------------

    def reload_sequences(self, sequence_files=None):
        def _all_sequence_files():
            return tuple(
                (f.relative, f.abspath)
                for f in fast_scan(self.path_sequences, search_filter=FAST_SCAN_REGEX_FILTER_FOR_PY_FILES)
            )

        for f_relative, f_absolute in (sequence_files or _all_sequence_files()):
            package_name = REGEX_PY_EXTENSION.sub('', f_relative).replace('/', '.')
            if package_name in self.sequences:
                importlib.reload(self.sequences[package_name])
            else:
                self.sequences[package_name] = importlib.import_module(f'{self.path_sequences}.{package_name}')
            self.pre_render_sequence[package_name]

    def pre_render_sequence(self, name):
        """
        Render a lighting sequence to a binary intermediary
        """
        log.info(f'PreRender {name}')

    def run_sequence(self, name):
        """
        Run a timing loop for a sequence
        """
        def _loop(framerate, filename, close_event):
            loop = Loop(framerate)
            loop.render = None  # TODO: render method
        p = multiprocessing.Process(target=_loop, args=(self.framerate, filename, close_event))
        p.start()
