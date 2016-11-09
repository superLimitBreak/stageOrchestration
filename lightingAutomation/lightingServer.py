import logging
log = logging.getLogger(__name__)

from multiprocessing import Queue

from ext.client_reconnect import SubscriptionClient
from ext.misc import file_scan_diff_thread


def serve(**kwargs):
    log.info('Serve {}'.format(kwargs))
    LightingServer(**kwargs)


class LightingServer(object):

    def __init__(self, **kwargs):

        self.network_event_queue = Queue()
        if kwargs.get('displaytrigger_host'):
            self.net = SubscriptionClient(host=kwargs['displaytrigger_host'], subscriptions=('lights', 'all'))
            self.net.recive_message = lambda msg: self.network_event_queue.put(msg)

        self.scan_update_event_queue = Queue()
        if 'scaninterval' in kwargs:
            self.scan_update_event_queue = file_scan_diff_thread(kwargs['path_sequences'], rescan_interval=kwargs['scaninterval'])

        #self.loop = Loop(kwargs['framerate'])
        #self.loop.render = self.render
        #self.loop.close = self.close
