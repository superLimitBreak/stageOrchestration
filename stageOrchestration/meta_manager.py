import logging
import copy
import os.path
from functools import reduce
from functools import partial
from calaldees.timecode import timecode_to_seconds, parse_timesignature

import yaml


log = logging.getLogger(__name__)

DEFAULT_META = {
    'name': 'Unknown',
    'bpm': 120,
    'timesignature': '4:4',
}


class MetaManager():
    """
    LightingSequnces and Events have metadata associated with them.
    This derives common details like timesigniture and bpm.

    Because meta is so light, there is little need to cache these details.
    """

    def __init__(self, path_sequences=None):
        self.path_sequences = path_sequences

    def get_meta(self, sequence):
        if hasattr(sequence, 'META'):
            meta = copy.copy(DEFAULT_META)
            meta.update(getattr(sequence, 'META'))
        else:
            meta = self._load_meta(sequence)

        # Create functions
        meta['get_time_func'] = partial(timecode_to_seconds, bpm=meta['bpm'], timesignature=parse_timesignature(meta['timesignature']))

        return meta

    def _load_meta(sequence_name):
        # Load/overlay yaml files
        def meta_yaml_reducer(accu, filename):
            filename = os.path.join(self.path_sequences, f'{filename}.yaml')
            if os.path.exists(filename):
                log.debug(f'Open meta {filename}')
                with open(filename, 'rt') as filehandle:
                    accu.update(yaml.safe_load(filehandle))
            return accu
        return reduce(meta_yaml_reducer, ('_default', sequence_name), copy.copy(DEFAULT_META))
