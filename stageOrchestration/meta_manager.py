import logging
import os.path
from functools import reduce
from functools import partial
from ext.music import get_time, parse_timesigniture

import yaml


log = logging.getLogger(__name__)


class MetaManager():
    """
    LightingSequnces and Events have metadata associated with them.
    This derives common details like timesigniture and bpm.

    Because meta is so light, there is little need to cache these details.
    """

    def __init__(self, path_sequences):
        self.path_sequences = path_sequences

    def get_meta(self, sequence_name):
        # Load/overlay yaml files
        def meta_yaml_reducer(accu, filename):
            filename = os.path.join(self.path_sequences, f'{filename}.yaml')
            if os.path.exists(filename):
                log.debug(f'Open meta {filename}')
                with open(filename, 'rt') as filehandle:
                    accu.update(yaml.load(filehandle))
            return accu
        meta = reduce(meta_yaml_reducer, ('_default', sequence_name), {})

        # Create functions
        meta['get_time_func'] = partial(get_time, timesigniture=parse_timesigniture(meta['timesignature']), bpm=meta['bpm'])

        return meta