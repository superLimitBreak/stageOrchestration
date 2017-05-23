import logging
import multiprocessing
import tempfile
from time import sleep

from ext.client_reconnect import SubscriptionClient
from ext.misc import file_scan_diff_thread, multiprocessing_process_event_queue, fast_scan, fast_scan_regex_filter, parse_rgb_color

from .output.realtime.timer_loop import timer_loop
from .output.realtime import RealtimeOutputManager
from .output.static import StaticOutputManager
from .render.sequence_manager import SequenceManager, FAST_SCAN_REGEX_FILTER_FOR_PY_FILES
from .model.device_collection_loader import device_collection_loader

log = logging.getLogger(__name__)


def serve(**kwargs):
    #log.info('Serve {}'.format(kwargs))
    server = LightingServer(**kwargs)
    server.run()


class LightingServer(object):

    def __init__(self, **kwargs):
        self.frame_rate = kwargs['framerate']

        self.tempdir = tempfile.TemporaryDirectory()

        self.network_event_queue = multiprocessing.Queue()
        if kwargs.get('displaytrigger_host'):
            self.net = SubscriptionClient(host=kwargs['displaytrigger_host'], subscriptions=('lights', 'all'))
            self.net.recive_message = lambda msg: self.network_event_queue.put(msg)

        self.scan_update_event_queue = multiprocessing.Queue()
        if 'scaninterval' in kwargs:
            self.scan_update_event_queue = file_scan_diff_thread(
                kwargs['path_sequences'],
                search_filter=FAST_SCAN_REGEX_FILTER_FOR_PY_FILES,
                rescan_interval=kwargs['scaninterval']
            )

        def _generate_device_collection_for_current_stage_description():
            return device_collection_loader(kwargs['path_stage_description'])

        self.device_collection = _generate_device_collection_for_current_stage_description()
        self.sequence_manager = SequenceManager(
            path_sequences=kwargs['path_sequences'],
            device_collection=_generate_device_collection_for_current_stage_description(),
            tempdir=self.tempdir.name,
            frame_rate=self.frame_rate,
        )

        output_settings = {
            'dmx_host': kwargs['dmx_host'],
            'dmx_mapping': kwargs['dmx_mapping'],
            'http_png_port': kwargs['http_png_port'],
            'json_send': None,
        }
        if hasattr(self, 'net'):
            output_settings['json_send'] = lambda data: self.net.send_message({'deviceid': 'light_visulisation', 'func': 'lightState', 'data': data})
            #print(data['light1']) #

        self.output_realtime = RealtimeOutputManager(self.device_collection, output_settings)
        self.output_static = StaticOutputManager(self.sequence_manager, output_settings)

        self.timer_process_queue = multiprocessing.Queue(1)
        self.timer_process = None
        self.timer_process_close_event = None

    # Event Handling -------------------------------------------------------

    def run(self):
        multiprocessing_process_event_queue({
            self.network_event_queue: self.network_event,
            self.scan_update_event_queue: self.sequence_manager.reload_sequences,
            self.timer_process_queue: self.frame_event,
        })
        # Blocks infinitely and is terminated by ctrl+c or exit event
        self.close()

    def close(self):
        self.stop_sequence()
        self.output_realtime.close()
        self.output_static.close()
        log.info('Removed temporary sequence files')
        self.tempdir.cleanup()


    def network_event(self, event):
        log.debug(event)
        func = event.get('func')
        if func == 'LightTiming.start':
            self.start_sequence(event.get("scene"))
        if func == 'lights.set':
            rgb = parse_rgb_color(event.get('value'))
            for device in self.device_collection.get_devices(event.get('device')):
                device.rgb = rgb
            self.output_realtime.update()
        if func == 'lights.clear':
            self.stop_sequence()
            self.device_collection.reset()
            self.output_realtime.update()

    def frame_event(self, buffer):
        self.device_collection.unpack(buffer, 0)
        self.output_realtime.update()

    # Render Loop --------------------------------------------------------------

    def stop_sequence(self):
        if self.timer_process_close_event:
            self.timer_process_close_event.set()
            self.timer_process.join()
            self.timer_process_close_event = None
            self.timer_process = None

    def start_sequence(self, sequence_module_name):
        """
        Run a timing loop for a sequence
        """
        self.stop_sequence()
        log.info(f'Start: {sequence_module_name}')

        self.timer_process_close_event = multiprocessing.Event()
        self.timer_process = multiprocessing.Process(
            target=timer_loop,
            args=(
                self.sequence_manager.get_persistent_sequence_filename(sequence_module_name),
                self.device_collection.pack_size,
                self.frame_rate,
                self.timer_process_close_event,
                self.timer_process_queue
            ),
        )
        self.timer_process.start()

