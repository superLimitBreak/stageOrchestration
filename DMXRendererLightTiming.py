import time
import yaml
import operator
import copy

import pytweening

from libs.misc import file_scan, list_neighbor_generator, parse_rgb_color, file_scan_diff_thread
from libs.music import parse_timesigniture, parse_timecode

from DMXBase import AbstractDMXRenderer, get_value_at

import logging
log = logging.getLogger(__name__)


class DMXRendererLightTiming(AbstractDMXRenderer):
    """
    Load a dataset of scenes and seqeucnes as dictionarys

    Scene = A lighting scene that has a duration in beats that can render it's state to a dmx_universe
    Sequence = A plain list of scenes to be played in order
    These are loaded from YAML datasets

    start/stop can be triggeded from an external system and reference any of the sequenes or scenes by name

    example start({'sequence':'THE YAML SEQUENCE FILENAME', 'bpm': 120})

    When start is called a start_time is recorded.
    Every time 'render' is called it gets the current time and works out the current 'beat' from the start time
    The correct scene is found in the sequence.
    The scenes 'render' method is called with the current 'beat' into the scene
    """

    DEFAULT_SCENE_NAME = 'none'
    DEFAULT_SEQUENCE_NAME = 'none'
    DEFAULT_BPM = 120.0
    DEFAULT_TIMESIGNITURE = "4:4"

    def __init__(self, path_config, path_scenes, path_sequences, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = self._open_yaml(path_config)
        self.scenes = self._open_path(path_scenes, SceneFactory(self.config).create_scene)
        self.sequences = self._open_path(path_sequences)

        #def onfilechange(changed_files):
        #    print(changed_files)
        #file_scan_diff_thread((path_scenes, path_sequences), onfilechange)

        self.bpm = self.DEFAULT_BPM
        self.timesigniture = parse_timesigniture(self.DEFAULT_TIMESIGNITURE)

        self.dmx_universe_previous = copy.copy(self.dmx_universe)

        self.stop()

    @staticmethod
    def _open_yaml(path, target_class=None):
        with open(path, 'rb') as file_handle:
            obj_data = yaml.load(file_handle)
            return target_class(obj_data) if target_class else obj_data

    @staticmethod
    def _open_path(path, target_class=None):
        """
        Open all yamls in a path by constructing an object for each file based on the 'target' class
        """
        objs = {}
        for file_info in file_scan(path, r'.*\.yaml$'):
            objs[file_info.file_no_ext] = DMXRendererLightTiming._open_yaml(file_info.absolute, target_class)
        return objs

    def start(self, data):
        """
        Originates from external call from trigger system
        """
        print(data)
        self.stop()
        self.time_start = time.time() - data.get('time_offset', 0)
        self.bpm = float(data.get('bpm', self.DEFAULT_BPM))
        self.timesigniture = parse_timesigniture(data.get('timesigniture', self.DEFAULT_TIMESIGNITURE))
        if data.get('sequence'):
            self.sequence = self.sequences[data.get('sequence')]
        if data.get('scene'):
            self.sequence = (self.scenes.get(data.get('scene', self.DEFAULT_SCENE_NAME)), )
        self.sequence_index = 0

    def stop(self, data={}):
        """
        Originates from external call from trigger system
        """
        self.time_start = 0
        self.sequence = ()
        self.sequence_index = None

    @property
    def sequence_index(self):
        return self._sequence_index
    @sequence_index.setter
    def sequence_index(self, index):
        self._sequence_index = index
        if self.sequence and self.sequence_index is not None:
            log.info('Rendering scene: {0}'.format(self.sequence[self.sequence_index]))

    @property
    def default_scene(self):
        return self.scenes.get(self.DEFAULT_SCENE_NAME)

    @property
    def default_sequence(self):
        return (self.default_scene, )

    @property
    def current_beat(self):
        return max(0.0, ((time.time() - self.time_start) / 60) * self.bpm if self.time_start else 0.0)

    @property
    def current_bar(self):
        return self.current_beat / self.timesigniture.bar

    @property
    def current_sequence_of_scenes(self):
        return (self.scenes.get(scene_name, ) for scene_name in self.sequence) if self.sequence else self.default_sequence

    def render(self, frame):
        scene, scene_beat, sequence_index = self.get_scene_at_beat(self.current_bar)
        if sequence_index is not self.sequence_index:
            self.sequence_index = sequence_index
            self.dmx_universe_previous = copy.copy(self.dmx_universe)
        scene.render(self.dmx_universe, self.dmx_universe_previous, scene_beat)
        return self.dmx_universe

    def get_scene_at_beat(self, current_beat):
        current_scene, beats_into_scene, sequence_index = get_value_at(self.current_sequence_of_scenes, current_beat, operator.attrgetter('total_beats'))
        if not current_scene:
            current_scene = self.default_scene
            beats_into_scene = beats_into_scene % self.default_scene.total_beats
        return current_scene, beats_into_scene, sequence_index


class SceneFactory(object):
    """
    This factory creates a Scene from a plain YAML data structure
    Separate out the YAML parsing and interpritation from the functional use of Scene
    """
    DEFAULT_DURATION = 4.0

    def __init__(self, config):
        self.config = config

    def create_scene(self, data):
        #\import pudb ; pu.db
        scene_items = self.parse_scene_order(data)
        #import pudb ; pu.db
        # Step though the dict items in order - rendering the desired output to 'previous' and 'target' states
        for previous_scene, current_scene, next_scene in list_neighbor_generator(scene_items):
            self.pre_render_scene_item(current_scene, previous_scene)
        return Scene(scene_items)

    def parse_scene_order(self, data):
        """
        Durations are 'dict string keys'. The keys need to be converted to floats.
        The keys need to be ordered and the scenes returned with calculated durations
        """
        if not data:
            return ()

        meta = data.pop('meta', {})
        timesigniture = parse_timesigniture(meta.get('timesigniture', '4:4'))
        num_scenes = len(data)

        def attempt_parse_key_timecode(value):
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
            try:
                return parse_timecode(value, timesigniture)
            except (AssertionError, ValueError, AttributeError) as e:
                pass
            return value
        # Surface the original key value in the dict (useful for debugging)
        for key, value in data.items():
            if value:
                value['key'] = key
        data_float_indexed = {attempt_parse_key_timecode(k): v for k, v in data.items()}
        assert len(data_float_indexed) == num_scenes
        sorted_keys = sorted(data_float_indexed.keys())
        assert len(sorted_keys) == num_scenes
        def normalise_duration(index):
            """
            Convert any time code or alias to a linear float value. e.g.
            '1.2' parses to -> 1.5
            'match_next' resolves to -> 4.0
            """
            key = sorted_keys[index]
            item = data_float_indexed[key]
            if not item:
                item = {'duration': 'auto'}
                data_float_indexed[key] = item
            duration = attempt_parse_key_timecode(item.get('duration'))
            if duration == 'match_next':
                duration = normalise_duration(index+1)
            if duration == 'match_prev':
                duration = normalise_duration(index-1)
            if isinstance(duration, str) and duration.startswith('match '):
                duration = normalise_duration(sorted_keys.index(float(duration.strip('match '))))
            if (not duration or duration == 'auto') and index < len(sorted_keys)-1:
                duration = sorted_keys[index+1] - key
            if not isinstance(duration, float):
                log.info('Unparsed duration: {0}'.format(duration))
                duration = self.DEFAULT_DURATION
            if duration != item.get('duration'):
                item['duration'] = duration
            return duration
        for index in range(len(sorted_keys)):
            normalise_duration(index)
        scene_items = []
        for key in sorted_keys:
            scene_item = data_float_indexed[key]
            assert scene_item and scene_item.get('duration') >= 0, "All scene must have durations. Something has failed in parsing. {0}:{1}".format(key, scene_item)
            scene_items.append(scene_item)
        return scene_items

    def pre_render_scene_item(self, current_scene, previous_scene):
        """
        Once the order of the items is known, we can iterate over the scenes
        calculating/prerendering the dmx state for each section
        This make seeking much faster
        """
        assert current_scene
        current_scene_dmx = current_scene.setdefault(Scene.SCENE_ITEM_DMX_STATE_KEY, {})
        # Aquire a reference to the previous DMX state
        if previous_scene:
            current_scene_dmx['previous'] = previous_scene.get(Scene.SCENE_ITEM_DMX_STATE_KEY, {})['target']

        # The target state is a copy of the previous state
        current_scene_dmx['target'] = copy.copy(current_scene_dmx.get('previous')) if current_scene_dmx.get('previous') else AbstractDMXRenderer.new_dmx_array()

        # Modify the target state based on this scene item
        self.render_state_dict(current_scene.get('state'), current_scene_dmx['target'])


    def render_state_dict(self, target_state_dict, dmx_universe_target):
        """
        Given a state dict in the form of
        {alias_name: value, alias_name2: value}
        and render that to a DMX array
        """
        if not target_state_dict:
            return

        # Render item
        def render_state_item(dmx_device_name, color_value):
            dmx_device = self.config['dmx_devices'].get(dmx_device_name)
            # Single light
            if dmx_device.get('type') == 'lightRGBW':
                color_value = self.config['colors'].get(color_value, parse_rgb_color(color_value)) if isinstance(color_value, str) else color_value
                for index, rgb_value in enumerate(color_value):
                    dmx_universe_target[index+dmx_device['index']] = min(255, int(rgb_value * 255))
            # Group alias
            elif dmx_device.get('type') == 'group':
                for group_item_dmx_device_name in dmx_device['group']:
                    render_state_item(group_item_dmx_device_name, color_value)

        # Render dict
        for dmx_device_name, color_value in target_state_dict.items():
            render_state_item(dmx_device_name, color_value)


class Scene(object):
    SCENE_ITEM_DMX_STATE_KEY = 'dmx'

    def __init__(self, scene_items):
        """
        Given a list of parsed scene_items (a plain list of dicts)
        Provide methods for redering that data
        """
        self.scene_items = scene_items
        self.total_beats = sum(scene_item['duration'] for scene_item in self.scene_items)

    def get_scene_item_beat(self, target_beat):
        return get_value_at(self.scene_items, target_beat, operator.itemgetter('duration'))

    def render(self, dmx_universe, dmx_universe_previous, beat):
        scene_item, beat_in_item, _ = self.get_scene_item_beat(beat)
        progress = beat_in_item / scene_item['duration']
        previous = scene_item.get(Scene.SCENE_ITEM_DMX_STATE_KEY, {}).get('previous') or dmx_universe_previous
        target = scene_item[Scene.SCENE_ITEM_DMX_STATE_KEY]['target']
        tween_function = getattr(pytweening, scene_item.get('tween', ''), lambda n: 1)

        assert len(dmx_universe) >= len(previous) and len(dmx_universe) >= len(target)
        for index in range(len(dmx_universe)):
            dmx_universe[index] = self._get_byte_tween_value(progress, previous[index], target[index], tween_function)

    def _get_byte_tween_value(self, progress, previous_value, target_value, tween_function):
        return max(0, min(255, previous_value + int((tween_function(progress) * (target_value - previous_value)))))
