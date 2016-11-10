import logging
import multiprocessing
import importlib
import os.path
import re

from ext.client_reconnect import SubscriptionClient
from ext.misc import file_scan_diff_thread, multiprocessing_process_event_queue, fast_scan, fast_scan_regex_filter

log = logging.getLogger(__name__)

REGEX_PY_EXTENSION = re.compile(r'\.py$')


def serve(**kwargs):
    log.info('Serve {}'.format(kwargs))
    server = LightingServer(**kwargs)
    server.run()


class LightingServer(object):

    def __init__(self, **kwargs):
        self.path_sequences = kwargs['path_sequences']
        self.sequences = {}
        self.reload_sequences()

        self.network_event_queue = multiprocessing.Queue()
        if kwargs.get('displaytrigger_host'):
            self.net = SubscriptionClient(host=kwargs['displaytrigger_host'], subscriptions=('lights', 'all'))
            self.net.recive_message = lambda msg: self.network_event_queue.put(msg)

        self.scan_update_event_queue = multiprocessing.Queue()
        if 'scaninterval' in kwargs:
            self.scan_update_event_queue = file_scan_diff_thread(self.path_sequences, rescan_interval=kwargs['scaninterval'])

    def run(self):
        multiprocessing_process_event_queue({
            self.network_event_queue: self.network_event,
            self.scan_update_event_queue: self.scan_update_event,
        })

    def network_event(self, event):
        log.info(event)

    def scan_update_event(self, sequence_files):
        self.reload_sequences(sequence_files)

    def reload_sequences(self, sequence_files=None):
        #importlib.invalidate_caches()
        for f_relative, f_absolute in (sequence_files or self._all_sequence_files):
            package_name = REGEX_PY_EXTENSION.sub('', f_relative).replace('/', '.')
            log.info(package_name)
            if package_name in self.sequences:
                importlib.reload(self.sequences[package_name])
            else:
                self.sequences[package_name] = importlib.import_module(f'{self.path_sequences}.{package_name}')

        # Temp guff for testing
        for m in self.sequences.values():
            log.info(m.VALUE)


    @property
    def _all_sequence_files(self):
        return tuple(
            (f.relative, f.abspath)
            for f in fast_scan(
                self.path_sequences,
                search_filter=fast_scan_regex_filter(file_regex=REGEX_PY_EXTENSION, ignore_regex=r'^_')
            )
        )

    #que = multiprocessing.Queue()
    #(input,[],[]) = select.select([que._reader],[],[])



    #self.loop = Loop(kwargs['framerate'])
    #self.loop.render = self.render
    #self.loop.close = self.close
