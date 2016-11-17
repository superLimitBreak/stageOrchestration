import logging
import multiprocessing
import importlib
import os.path
import re
import tempfile
from time import sleep

import progressbar

from ext.attribute_packer import PersistentFramePacker
from ext.client_reconnect import SubscriptionClient
from ext.misc import file_scan_diff_thread, multiprocessing_process_event_queue, fast_scan, fast_scan_regex_filter

from .render_sequence import render_sequence
from .renderers.render_loop import render_loop
from .model.device_collection_loader import device_collection_loader

log = logging.getLogger(__name__)

REGEX_PY_EXTENSION = re.compile(r'\.py$')
FAST_SCAN_REGEX_FILTER_FOR_PY_FILES = fast_scan_regex_filter(file_regex=REGEX_PY_EXTENSION, ignore_regex=r'^_')


def serve(**kwargs):
    log.info('Serve {}'.format(kwargs))
    server = LightingServer(**kwargs)
    server.run()


class LightingServer(object):

    def __init__(self, **kwargs):
        self.frame_rate = kwargs['framerate']
        self.path_sequences = kwargs['path_sequences']

        self.device_collection = device_collection_loader(kwargs['path_stage_description'])

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

        self.render_process_queue = multiprocessing.Queue(1)
        self.render_process = None
        self.render_process_close_event = None

        self.tempdir = tempfile.TemporaryDirectory()
        self.sequences = {}

        self.reload_sequences()

    # File Handling --------------------------------------------------------
    def _get_persistent_sequence_filename(self, package_name):
        return os.path.join(self.tempdir.name, package_name)

    # Event Handling -------------------------------------------------------

    def run(self):
        multiprocessing_process_event_queue({
            self.network_event_queue: self.network_event,
            self.scan_update_event_queue: self.scan_update_event,
            self.render_process_queue: self.render_frame_event,
        })
        # Blocks infinitely and is terminated by ctrl+c or exit event
        self.close()

    def close(self):
        log.info('Removed temporary sequence files')
        self.stop_sequence()
        self.tempdir.cleanup()

    def network_event(self, event):
        log.info(event)
        if event.get('func') == 'LightTiming.start':
            self.run_sequence(event.get("scene"))

    def scan_update_event(self, sequence_files):
        self.reload_sequences(sequence_files)

    def render_frame_event(self, data):
        log.debug('render_frame_event')
        log.debug(data)

    # Sequences -------------------------------------------------------------

    def reload_sequences(self, sequence_files=None):
        """
        Traps for the Unwary in Python’s Import System
          http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html
        """

        def _all_sequence_files():
            return tuple(
                (f.relative, f.abspath)
                for f in fast_scan(self.path_sequences, search_filter=FAST_SCAN_REGEX_FILTER_FOR_PY_FILES)
            )

        bar_sequence_name_label = progressbar.FormatCustomText('%(sequence_name)-20s', {'sequence_name': ''})
        bar = progressbar.ProgressBar(
            widgets=(
                'Rendering: ', bar_sequence_name_label, ' ', progressbar.Bar(marker='=', left='[', right=']'),
            ),
        )

        for f_relative, f_absolute in bar(sequence_files or _all_sequence_files()):
            bar_sequence_name_label.update_mapping(sequence_name=f_relative)
            self._render_sequence_module(
                self._load_sequence_module(f_relative),
            )
            sleep(1)  # TODO: Temp remove

    def _load_sequence_module(self, f_relative):
        package_name = REGEX_PY_EXTENSION.sub('', f_relative).replace('/', '.')
        if package_name in self.sequences:
            importlib.reload(self.sequences[package_name])
        else:
            self.sequences[package_name] = importlib.import_module(f'{self.path_sequences}.{package_name}')
        sequence_module = self.sequences[package_name]
        setattr(sequence_module, '_sequence_name', sequence_module.__name__.replace(f'{sequence_module.__package__}.', ''))
        return sequence_module

    def _render_sequence_module(self, sequence_module):
        log.debug('Rendering sequence_module {}'.format(sequence_module._sequence_name))
        sequence_filename = self._get_persistent_sequence_filename(sequence_module._sequence_name)
        packer = PersistentFramePacker(self.device_collection, sequence_filename)
        render_sequence(
            packer=packer,
            sequence_module=sequence_module,
            device_collection=self.device_collection,
        )
        packer.close()
        assert os.path.exists(sequence_filename), f'Should have generated sequence file {sequence_filename}'

    # Render Loop --------------------------------------------------------------

    def stop_sequence(self):
        if self.render_process_close_event:
            self.render_process_close_event.set()
            self.render_process.join()
            self.render_process_close_event = None
            self.render_process = None

    def run_sequence(self, sequence_module_name):
        """
        Run a timing loop for a sequence
        """
        self.stop_sequence()

        self.render_process_close_event = multiprocessing.Event()
        self.render_process = multiprocessing.Process(
            target=render_loop,
            args=(
                self._get_persistent_sequence_filename(sequence_module_name),
                self.device_collection.pack_size,
                self.frame_rate,
                self.render_process_close_event,
                self.render_process_queue
            ),
        )
        self.render_process.start()

