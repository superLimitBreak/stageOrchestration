import logging
import multiprocessing
import tempfile
import time
import json
import traceback

from calaldees.net.client_reconnect import SubscriptionClient
from calaldees.misc import file_scan_diff_thread, multiprocessing_process_event_queue, fast_scan, fast_scan_regex_filter, parse_rgb_color
from calaldees.process import SingleOutputStopableProcess
from calaldees.timecode import next_frame_from_timecode

from .frame_count_loop import frame_count_loop
from .lighting.output.realtime.dmx import RealtimeOutputDMX
from .lighting.output.realtime.frame_reader import FrameReader
from .lighting.output.static.png import StaticOutputPNG
from .lighting.model.device_collection_loader import device_collection_loader
from .events.model.triggerline import TriggerLine

from .sequence_manager import SequenceManager, FAST_SCAN_REGEX_FILTER_FOR_PY_FILES


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
        else:
            class NullSubscriptionClient:
                def send_message(self, *args, **kwargs):
                    pass
            self.net = NullSubscriptionClient()

        self.scan_update_event_queue = multiprocessing.Queue()
        if 'scaninterval' in kwargs:
            self.scan_update_event_queue = file_scan_diff_thread(
                self.options['path_sequences'],
                search_filter=FAST_SCAN_REGEX_FILTER_FOR_PY_FILES,
                rescan_interval=self.options['scaninterval']
            )

        def load_device_collection():
            return device_collection_loader(kwargs['path_stage_description'])
        self.options['load_device_collection'] = load_device_collection

        # get_media_duration_func
        if self.options.get('path_media'):
            from .events.media_utils import MediaInfo
            media_info = MediaInfo(self.options.get('path_media'))
            self.options['get_media_duration_func'] = lambda filename: media_info.metadata(filename).get('duration')
        else:
            def _get_media_duration_func(filename):
                raise Exception('path_media not provided in config')
            self.options['get_media_duration_func'] = _get_media_duration_func

        self.device_collection = load_device_collection()
        self.sequence_manager = SequenceManager(**self.options)
        self.sequence_manager.reload_sequences()
        self.static_png_server = StaticOutputPNG(self.options) if self.options.get('http_png_port') else None
        self.dmx = RealtimeOutputDMX(
            host=self.options['dmx_host'],
            mapping_config_filename=self.options['dmx_mapping'],
        )

        self.frame_count_process = SingleOutputStopableProcess(frame_count_loop)
        self.current_sequence = {'module_name': '', 'module_hash': ''}
        self.frame_reader = None
        self.triggerline_renderer = None

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
        self.clear_sequence()
        self.frame_event()
        if self.static_png_server:
            self.static_png_server.close()
        self.tempdir.cleanup()

    def network_event(self, event):
        log.debug(f'network_event {event}')
        func = event.get('func')
        #try:
        if func == 'lights.load_sequence':
            self.load_sequence(sequence_module_name=event.get('sequence_module_name'))
        if func == 'lights.start_sequence':
            self.start_sequence(sequence_module_name=event.get('sequence_module_name'), timecode=event.get('timecode'))
        if func == 'lights.single_frame_at_timecode':
            self.frame_event(frame=next_frame_from_timecode(event.get('timecode'), self.options['framerate']))
        if func == 'lights.pause':
            self.pause_sequence()
        if func == 'lights.clear':
            self.clear_sequence()
            self.current_sequence['module_name'] = ''
            self.current_sequence['module_hash'] = ''
            self.frame_event()
        if func == 'lights.set':
            rgb = parse_rgb_color(event.get('value'))
            for device in self.device_collection.get_devices(event.get('device')):
                device.rgb = rgb
            self.frame_event()
        #except Exception as ex:
        #    traceback.print_exc()

    def scan_update_event(self, sequence_files):
        log.debug(f'scan_update_event {sequence_files}')
        self.sequence_manager.reload_sequences(sequence_files)
        self.current_sequence['module_hash'] = self.sequence_manager.get_rendered_hash(self.current_sequence['module_name'])
        self.net.send_message({
            'deviceid': self.DEVICEID_VISULISATION,
            'func': 'scan_update_event',
            'sequence_files': tuple(relative.replace('.py', '') for relative, absolute in sequence_files),
            **self.current_sequence,
        })

    def frame_event(self, frame=None):
        triggers_at = ()
        light_state = ()

        if frame:
            self.device_collection.unpack(self.frame_reader.read_frame(frame), 0)
            triggers_at = {
                'json_state_continuous': self.triggerline.get_triggers_at,
                'json_single_triggers': self.triggerline_renderer.get_triggers_at,
            }.get(self.options['output_mode'])(frame / self.options['framerate'])

        light_state = {
            'json_state_continuous': ({
                'deviceid': self.DEVICEID_VISULISATION,
                'func': 'lightState',
                'state': self.device_collection.todict(),
                'timecode': frame / self.options['framerate'] if frame else 0,
                **self.current_sequence,
            }, ),
        }.get(self.options['output_mode'], light_state)

        self.net.send_message(*light_state, *triggers_at)
        self.dmx.send(self.device_collection)

    def sequence_end_event():
        pass  # TODO: we need some mechanisum of knowing when a render is finsihed


    # Render Loop --------------------------------------------------------------

    def load_sequence(self, sequence_module_name=None):
        sequence_module_name = sequence_module_name or self.current_sequence['module_name']

        self.clear_sequence()

        self.current_sequence['module_name'] = sequence_module_name
        self.current_sequence['module_hash'] = self.sequence_manager.get_rendered_hash(sequence_module_name)
        log.info(f'load_sequence: {sequence_module_name}')
        # frame_reader points at sequence binary file
        self.frame_reader = FrameReader(
            self.sequence_manager.get_rendered_filename(sequence_module_name),
            self.device_collection.pack_size,
        )
        # triggerline holds a list of upcoming triggers in a timeline
        with open(self.sequence_manager.get_rendered_trigger_filename(sequence_module_name), 'rt') as filehandle:
            self.triggerline = TriggerLine(json.load(filehandle))
            self.triggerline_renderer = self.triggerline.get_render()

    def start_sequence(self, sequence_module_name=None, timecode=None):
        sequence_module_name = sequence_module_name or self.current_sequence['module_name']
        timecode = timecode or 0

        self.load_sequence(sequence_module_name=sequence_module_name)

        log.info(f'start_sequence: {sequence_module_name} at {timecode}')
        # frame_count_process is bound to self.frame_event each frame tick
        self.frame_count_process.start(self.frame_reader.frames, self.options['framerate'], title=sequence_module_name, timecode=timecode)

    def pause_sequence(self):
        self.frame_count_process.stop()
        self.device_collection.reset()

    def clear_sequence(self):
        self.pause_sequence()
        self.triggerline_renderer = None  # self.triggerline_renderer.reset()
        if self.frame_reader:
            self.frame_reader.close()
            self.frame_reader = None
