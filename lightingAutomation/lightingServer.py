import logging
import multiprocessing
import importlib
import os.path
import re
import tempfile

import progressbar

from ext.attribute_packer import PersistentFramePacker
from ext.client_reconnect import SubscriptionClient
from ext.misc import file_scan_diff_thread, multiprocessing_process_event_queue, fast_scan, fast_scan_regex_filter

from .render_sequence import render_sequence
from .render_loop import render_loop

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
        self.path_sequences = kwargs['path_sequences']
        self.path_stage_description = kwargs['path_stage_description']

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

        self.tempdir = tempfile.TemporaryDirectory()
        self.sequences = {}
        self.reload_sequences()

    # File Handling --------------------------------------------------------
    def _get_filename(self, package_name):
        return os.path.join(self.tempdir.name, package_name)

    # Event Handling -------------------------------------------------------

    def run(self):
        multiprocessing_process_event_queue({
            self.network_event_queue: self.network_event,
            self.scan_update_event_queue: self.scan_update_event,
        })
        self.close()

    def close(self):
        self.stop_sequence()
        self.tempdir.cleanup()

    def network_event(self, event):
        log.info(event)

    def scan_update_event(self, sequence_files):
        self.reload_sequences(sequence_files)

    # Sequences -------------------------------------------------------------

    def reload_sequences(self, sequence_files=None):
        """
        Traps for the Unwary in Python’s Import System
          http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html
        """

        bar = progressbar.ProgressBar(
            widgets=(
                'Rendering Sequences: ', progressbar.Counter(),
                ' ', progressbar.Bar(),
                ' ', progressbar.Percentage(),
                ' ', progressbar.ETA(),
            ),
            #redirect_stdout=True,
            #redirect_stderr=True,
        )

        def _all_sequence_files():
            return tuple(
                (f.relative, f.abspath)
                for f in fast_scan(self.path_sequences, search_filter=FAST_SCAN_REGEX_FILTER_FOR_PY_FILES)
            )

        device_collection = device_collection_loader(self.path_stage_description)

        for f_relative, f_absolute in bar(sequence_files or _all_sequence_files()):
            package_name = REGEX_PY_EXTENSION.sub('', f_relative).replace('/', '.')
            if package_name in self.sequences:
                importlib.reload(self.sequences[package_name])
            else:
                self.sequences[package_name] = importlib.import_module(f'{self.path_sequences}.{package_name}')

            packer = PersistentFramePacker(self._get_filename(package_name))
            render_sequence(
                packer=packer,
                sequence_module=self.sequences[package_name],
                device_collection=device_collection,
            )
            packer.close()

    # Render Loop --------------------------------------------------------------

    def stop_sequence(self):
        if self.render_process_close_event:
            self.render_process_close_event.set()
            self.render_process.join()
            self.render_process_close_event = None
            self.render_process = None

    def run_sequence(self, name):
        """
        Run a timing loop for a sequence
        """
        self.stop_sequence()

        self.render_process_close_event = multiprocessing.Event()
        self.render_process = multiprocessing.Process(
            target=render_loop,
            args=(self.path_stage_description, self._get_filename(name), self.framerate, self.render_process_close_event)
        )
        self.render_process.start()
