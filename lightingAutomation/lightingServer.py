import logging
import multiprocessing

from ext.client_reconnect import SubscriptionClient
from ext.misc import file_scan_diff_thread, multiprocessing_process_event_queue

log = logging.getLogger(__name__)


def serve(**kwargs):
    log.info('Serve {}'.format(kwargs))
    server = LightingServer(**kwargs)
    server.run()


class LightingServer(object):

    def __init__(self, **kwargs):

        self.network_event_queue = multiprocessing.Queue()
        if kwargs.get('displaytrigger_host'):
            self.net = SubscriptionClient(host=kwargs['displaytrigger_host'], subscriptions=('lights', 'all'))
            self.net.recive_message = lambda msg: self.network_event_queue.put(msg)

        self.scan_update_event_queue = multiprocessing.Queue()
        if 'scaninterval' in kwargs:
            self.scan_update_event_queue = file_scan_diff_thread(kwargs['path_sequences'], rescan_interval=kwargs['scaninterval'])

    def run(self):
        multiprocessing_process_event_queue({
            self.network_event_queue: self.network_event,
            self.scan_update_event_queue: self.scan_update_event,
        })

    def network_event(self, event):
        log.info(event)

    def scan_update_event(self, event):
        log.info(event)


    #que = multiprocessing.Queue()
    #(input,[],[]) = select.select([que._reader],[],[])



    #self.loop = Loop(kwargs['framerate'])
    #self.loop.render = self.render
    #self.loop.close = self.close
