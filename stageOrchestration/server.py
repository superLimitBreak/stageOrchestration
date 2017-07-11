import logging
import multiprocessing
import tempfile
from time import sleep

from ext.client_reconnect import SubscriptionClient
from ext.misc import file_scan_diff_thread, multiprocessing_process_event_queue, fast_scan, fast_scan_regex_filter, parse_rgb_color
from ext.process import SingleOutputStopableProcess



from .frame_count_loop import frame_count_loop
from .lighting.output.realtime import RealtimeOutputManager
from .lighting.output.realtime.frame_reader import FrameReader
from .lighting.output.static import StaticOutputManager
from .lighting.render.sequence_manager import SequenceManager, FAST_SCAN_REGEX_FILTER_FOR_PY_FILES
from .lighting.model.device_collection_loader import device_collection_loader
from .events.model.eventline_loader import eventline_loader


log = logging.getLogger(__name__)


def serve(**kwargs):
    #log.info('Serve {}'.format(kwargs))
    server = StageOrchestrationServer(**kwargs)
    server.run()


class StageOrchestrationServer(object):
    DEVICEID_VISULISATION = 'light_visulisation'

    def __init__(self, **kwargs):
        self.options = kwargs
        self.tempdir = tempfile.TemporaryDirectory()
        self.options['tempdir'] = self.tempdir.name

        self.network_event_queue = multiprocessing.Queue()
        if kwargs.get('displaytrigger_host'):
            self.net = SubscriptionClient(host=kwargs['displaytrigger_host'], subscriptions=('lights', 'all'))
            self.net.receive_message = lambda msg: self.network_event_queue.put(msg)

        self.scan_update_event_queue = multiprocessing.Queue()
        if 'scaninterval' in kwargs:
            self.scan_update_event_queue = file_scan_diff_thread(
                self.options['path_sequences'],
                search_filter=FAST_SCAN_REGEX_FILTER_FOR_PY_FILES,
                rescan_interval=self.options['scaninterval']
            )

        self.device_collection = device_collection_loader(kwargs['path_stage_description'])
        self.sequence_manager = SequenceManager(**self.options)
        self.output_static = StaticOutputManager(self.options)

        if hasattr(self, 'net'):
            self.options['json_send'] = lambda data: self.net.send_message({
                'deviceid': self.DEVICEID_VISULISATION,
                'func': 'lightState',
                'data': data,
            })
            #print(data['light1']) #
        self.lighting_output_realtime = RealtimeOutputManager(self.device_collection, self.options)

        self.frame_count_process = SingleOutputStopableProcess(frame_count_loop)
        self.frame_reader = None

    # Event Handling -------------------------------------------------------

    def run(self):
        multiprocessing_process_event_queue({
            self.network_event_queue: self.network_event,
            self.scan_update_event_queue: self.scan_update_event,
            self.frame_count_process.queue: self.frame_event,
        })
        # Blocks infinitely and is terminated by ctrl+c or exit event
        self.close()

    def close(self):
        self.frame_count_process.stop()
        self.lighting_output_realtime.close()
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
            self.lighting_output_realtime.update()
        if func == 'lights.clear':
            self.frame_count_process.stop()
            self.device_collection.reset()
            self.lighting_output_realtime.update()

    def scan_update_event(self, sequence_files):
        self.sequence_manager.reload_sequences(sequence_files)
        self.net.send_message({
            'deviceid': self.DEVICEID_VISULISATION,
            'func': 'scan_update_event',
            'sequence_files': tuple(relative.replace('.py', '') for relative, absolute in sequence_files),
        })

    def frame_event(self, frame):
        self.device_collection.unpack(self.frame_reader.read_frame(frame), 0)
        self.lighting_output_realtime.update()
        self.net.send_message(*self.eventline.render(frame / self.options['framerate']))

    # Render Loop --------------------------------------------------------------

    def start_sequence(self, sequence_module_name):
        log.info(f'Start: {sequence_module_name}')
        if self.frame_reader:
            self.frame_reader.close()
            self.frame_reader = None
        # frame_reader points at sequence binary file
        self.frame_reader = FrameReader(
            self.sequence_manager.get_filename(sequence_module_name),
            self.device_collection.pack_size,
        )
        # eventline holds a list of upcoming triggers in a timeline
        self.eventline = eventline_loader(os.path.join(kwargs['path_stage_description'], f'{sequence_module_name}.yaml'))
        # frame_count_process is bound to self.frame_event each frame tick
        self.frame_count_process.start(self.frame_reader.frames, self.options['framerate'])
