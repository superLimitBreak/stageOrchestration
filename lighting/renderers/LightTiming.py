import os.path
import time
import operator
import copy

import pytweening

from libs.misc import file_scan, list_neighbor_generator, file_scan_diff_thread
from libs.music import parse_timesigniture, timecode_to_beat, beat_to_timecode, get_beat

from lighting import AbstractDMXRenderer, get_value_at, open_path

import logging
log = logging.getLogger(__name__)

DEFAULT_TIMESIGNITURE = "4:4"
DEFAULT_TIMESIGNITURE_ = parse_timesigniture(DEFAULT_TIMESIGNITURE)


class LightTiming(AbstractDMXRenderer):
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

    PATH_SCENES_FOLDER = 'scenes'
    PATH_SEQUENCE_FOLDER = 'sequences'

    DEFAULT_SCENE_NAME = 'none'
    DEFAULT_SEQUENCE_NAME = 'none'
    DEFAULT_BPM = 120.0

    def __init__(self, config, yamlpath, rescan_interval=2.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.yamlpath = yamlpath

        self._sequence_index = None
        self.time_mutator = None
        self.sequence = None
        self.time_start = None
        self.bpm = None

        file_scan_diff_thread(yamlpath, lambda *args, **kwargs: self.reload(), rescan_interval=rescan_interval)
        self.reload()
        self.stop()

    def reload(self):
        log.info('Loading scenes {0}'.format(self.yamlpath))
        try:
            self.scenes = open_path(os.path.join(self.yamlpath, self.PATH_SCENES_FOLDER), SceneParser(self.config).create_scene)
            self.sequences = open_path(os.path.join(self.yamlpath, self.PATH_SEQUENCE_FOLDER))
        except Exception as e:
            log.error('Failed to load scenes, data is buggered. Lets get out of here')
            exit(2)

        self.dmx_universe_previous = copy.copy(self.dmx_universe)

    @property
    def time_offset(self):
        return self.config.config.get('time_offset', 0)

    def start(self, data):
        """
        Originates from external call from trigger system
        """
        log.info(data)
        self.stop()
        self.time_start = time.time() - data.get('time_offset', 0) - self.time_offset
        self.bpm = float(data.get('bpm', self.DEFAULT_BPM))
        self.timesigniture = parse_timesigniture(data.get('timesigniture', DEFAULT_TIMESIGNITURE))
        if data.get('sequence'):
            sequence_name = data.get('sequence')
            assert sequence_name in self.sequences, '{0} is not a known sequence'.format(sequence_name)
            self.sequence = self.sequences[sequence_name]
        if data.get('scene'):
            # Single scene - Fake the sequence list by inserting the name of the single scene required
            self.sequence = (data.get('scene', self.DEFAULT_SCENE_NAME), )
        self.sequence_index = 0

    def stop(self, data={}):
        """
        Originates from external call from trigger system
        """
        self.time_start = 0
        self.time_mutator = 0
        self.sequence = ()
        self.sequence_index = None
        self.bpm = self.DEFAULT_BPM
        self.timesigniture = DEFAULT_TIMESIGNITURE_

    def seek(self, data={}):
        self._seek(data.get('currentTime', 0))

    def _seek(self, time_offset):
        if (time.time() - self.time_start) < 0.1:
            log.info('Seek recived within 100ms of start - Assuming this is a bounceback from test_audio - applying automatic time mutator of {0}s'.format(time_offset))
            self.time_mutator = time_offset
        self.time_start = time.time() - time_offset
        log.info('seek {0}'.format(time_offset))

    @property
    def sequence_index(self):
        return self._sequence_index
    @sequence_index.setter
    def sequence_index(self, index):
        if self.sequence_index is index:
            return
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
        if not self.time_start:
            return 0.0
        return get_beat(time.time() - self.time_mutator, self.bpm, time_start=self.time_start)

    @property
    def current_bar(self):
        return self.current_beat / self.timesigniture.bar

    @property
    def current_sequence_of_scenes(self):
        return (self.scenes.get(scene_name, ) for scene_name in self.sequence) if self.sequence else self.default_sequence

    def render(self, frame):
        # print(beat_to_timecode(self.current_bar, self.timesigniture), self.current_bar)
        scene, scene_beat, sequence_index = self.get_scene_at_beat(self.current_bar)
        self.sequence_index = sequence_index
        # self.dmx_universe_previous = copy.copy(self.dmx_universe)
        scene.render(self.dmx_universe, scene_beat)  # self.dmx_universe_previous,  # previous universe was taken out to simplify scene parsing. Every scene was now self contained. We might reinstate the previous state at a later date
        return self.dmx_universe

    def get_scene_at_beat(self, current_beat):
        current_scene, beats_into_scene, sequence_index = get_value_at(self.current_sequence_of_scenes, current_beat, operator.attrgetter('total_beats'))
        if not current_scene:
            current_scene = self.default_scene
            beats_into_scene = beats_into_scene % self.default_scene.total_beats
        return current_scene, beats_into_scene, sequence_index


class SceneParser(object):
    """
    This factory creates a Scene from a plain YAML data structure
    Separate out the YAML parsing and interpritation from the functional use of Scene

    Processing scenes:
        * Parse string 'keys' as timecodes into linear floats to represent time
        * Sort the items in a scene by time
        * Iterate through each scene item in order pre-rendering the dmx state before and after

    Input structure (plain dict):
        {
            meta:
                optional extra keys to support processing
            '0.0.0':
                state_start (OPTIONAL):
                state (OPTIONALish):
                    LIGHT_ALIAS: COLOR_ALIAS
                tween: TWEEN_FUNCTIONNAME (see pytweening for list)
            '1.2.0':
                same structure as above
            '2.0.0':
                None
        }

    Output structure 'scene_items' (ordered list):
        [
            {
                dmx:
                    previous: BYTEARRAY
                    target: BYTEARRAY
                key: '0.0.0'
                state: same as source - unneeded, just here for reference
                state_start: same as source
                tween: TWEEN_FUNCTIONNAME same as source
                duration: 1.5
            },
            {
                same structure as above
                duration: 0.5
            },
            {
                dmx:
                    previous: BYTEARRAY (copied from previous sceneitem)
                    target: BYEARRAY (copied from this sceneitem)
                duration: 0 (by default)
            }
        ]

        This processing could be in a separate file and could be unit tested
    """
    DEFAULT_DURATION = 0.0

    MUTED_DEVICES = ('use', 'name')

    def __init__(self, config):
        self.config = config
        self.dmx_universe_alias = {}
        self.mute_devices = []

    def create_scene(self, data):
        if not data:
            return Scene([])
        meta = data.pop('meta', {})
        timesigniture = parse_timesigniture(meta.get('timesigniture', '4:4'))
        self.mute_devices = tuple(meta.get('mute_devices', ())) + self.MUTED_DEVICES
        # TODO: Derive all muted devices by steping down the device alias tree

        scene_items = self.parse_scene_order(data, timesigniture)
        # Step though the dict items in order - rendering the desired output to 'previous' and 'target' states
        for previous_scene_item, current_scene_item, next_scene_item in list_neighbor_generator(scene_items):
            self.pre_render_scene_item(current_scene_item, previous_scene_item)
        return Scene(scene_items, timesigniture)

    def parse_scene_order(self, data, timesigniture):
        """
        Durations are 'dict string keys'. The keys need to be converted to floats.
        The keys need to be ordered and the scenes returned with calculated durations
        """
        if not data:
            return ()

        num_scenes = len(data)

        def attempt_parse_key_timecode(value):
            if not value:
                return value
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
            try:
                return timecode_to_beat(value, timesigniture)
            except (AssertionError, ValueError, AttributeError):
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
                #log.info('Unparsed duration: {0}'.format(duration))
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

    def pre_render_scene_item(self, current_scene_item, previous_scene_item):
        """
        Once the order of the items is known, we can iterate over the scenes
        calculating/prerendering the dmx state for each section
        This make seeking much faster
        """
        assert current_scene_item
        current_scene_dmx = current_scene_item.setdefault(Scene.SCENE_ITEM_DMX_STATE_KEY, {})
        # Aquire a reference to the previous DMX state
        current_scene_dmx['previous'] = copy.copy(previous_scene_item.get(Scene.SCENE_ITEM_DMX_STATE_KEY, {})['target']) if previous_scene_item else AbstractDMXRenderer.new_dmx_array()
        # The target state is a copy of the previous state
        current_scene_dmx['target'] = copy.copy(current_scene_dmx['previous'])

        # Modify the starting/previous state based on any overrides in this scene (this is a shortcut feature as I kept requireing this)
        self.render_state_dict(current_scene_item.get('state_start'), current_scene_dmx['previous'])
        # Modify the target state based on this scene item
        self.render_state_dict(current_scene_item.get('state'), current_scene_dmx['target'])


    def render_state_dict(self, target_state, dmx_universe_target):
        """
        Given a state dict in the form of
        {alias_name: value, alias_name2: value}
        and render that to a DMX array

        This needs refactoring.
        Maybe abstract each light into an object that has it's own color function to convert it to it's own color space?
        """
        if not target_state:
            return
        # Copy the alias over this bytearray
        if isinstance(target_state, str):
            target_state = {'use': target_state}
        alias_name = target_state.get('use')
        if alias_name:
            assert alias_name in self.dmx_universe_alias, "alias '{0}' not defined".format(alias_name)
            dmx_universe_target[:] = self.dmx_universe_alias[alias_name]

        # Render items
        for dmx_device_name, color_value in target_state.items():
            self.config.render_device(dmx_universe_target, dmx_device_name, color_value)
        # Mute items
        for dmx_device_name in self.mute_devices:
            self.config.render_device(dmx_universe_target, dmx_device_name, None)

        # Add an alias for this state if a name is provided
        if target_state.get('name'):
            self.dmx_universe_alias[target_state.get('name')] = dmx_universe_target


class Scene(object):
    SCENE_ITEM_DMX_STATE_KEY = 'dmx'

    def __init__(self, scene_items, timesigniture=DEFAULT_TIMESIGNITURE_):
        """
        Given a list of parsed scene_items (a plain list of dicts)
        Provide methods for redering that data

        timesigniture is only used for debug printing
        """
        self.scene_items = scene_items
        self.total_beats = sum(scene_item['duration'] for scene_item in self.scene_items)
        self.timesigniture = timesigniture

    def get_scene_item_beat(self, target_beat):
        return get_value_at(self.scene_items, target_beat, operator.itemgetter('duration'))

    def render(self, dmx_universe, beat):
        #log.debug(beat_to_timecode(beat, self.timesigniture), beat)
        scene_item, beat_in_item, _ = self.get_scene_item_beat(beat)
        progress = beat_in_item / scene_item['duration']
        previous = scene_item.get(Scene.SCENE_ITEM_DMX_STATE_KEY, {}).get('previous')  # or dmx_universe_previous
        target = scene_item[Scene.SCENE_ITEM_DMX_STATE_KEY]['target']
        tween_function = getattr(pytweening, scene_item.get('tween', ''), lambda n: 1)

        assert len(dmx_universe) >= len(previous) and len(dmx_universe) >= len(target)
        for index in range(len(dmx_universe)):
            dmx_universe[index] = self._get_byte_tween_value(progress, previous[index], target[index], tween_function)

    def _get_byte_tween_value(self, progress, previous_value, target_value, tween_function):
        return max(0, min(255, previous_value + int((tween_function(progress) * (target_value - previous_value)))))
