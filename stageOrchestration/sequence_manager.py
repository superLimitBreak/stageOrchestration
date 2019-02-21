import sys
import logging
import re
import os.path
import importlib
import json
from pathlib import PurePath


import progressbar

from calaldees.files.scan import fast_scan, fast_scan_regex_filter, hashfile
from calaldees.attribute_packer import PersistentFramePacker

from stageOrchestration.meta_manager import MetaManager
from stageOrchestration.render_sequence import render_sequence

REGEX_PY_EXTENSION = re.compile(r'\.py$')
FAST_SCAN_REGEX_FILTER_FOR_PY_FILES = fast_scan_regex_filter(file_regex=REGEX_PY_EXTENSION, ignore_regex=r'^_')

log = logging.getLogger(__name__)


class SequenceManager(object):

    def __init__(self, path_sequences=None, tempdir=None, framerate=None, load_device_collection=None, **kwargs):
        assert os.path.isdir(path_sequences)
        assert os.path.exists(tempdir)
        assert framerate
        assert kwargs['get_media_duration_func'].__call__

        self.path_sequences = PurePath(path_sequences)
        sys.path.append(str(self.path_sequences.parent))  # Can't load modules from path. Must add a system path. Thanks Python.
        self.tempdir = tempdir
        self.framerate = framerate
        self.get_media_duration_func = kwargs['get_media_duration_func']

        self.device_collection = load_device_collection()
        assert self.device_collection.devices
        self.meta_manager = MetaManager(path_sequences)

        self.sequence_modules = {}

    def get_rendered_trigger_filename(self, sequence):
        """
        TODO: I've made the SequenceManager derive the .trigger.yaml filename
        This is because the .py sequence could/should in future contain the triggers.
        """
        return self.get_rendered_filename(sequence, suffix='.triggers.yaml')

    def get_rendered_filename(self, sequence, suffix=''):
        """
        Can be passed a module, sequence_name or filename
        """
        if hasattr(sequence, '_sequence_name'):
            sequence = sequence._sequence_name
        if not os.path.isfile(sequence):
            sequence = os.path.join(self.tempdir, f'{sequence}{suffix}')
        return sequence

    def get_rendered_hash(self, sequence):
        return hashfile(self.get_rendered_filename(sequence)) + hashfile(self.get_rendered_trigger_filename(sequence))

    def get_packer(self, sequence, assert_exists=True):
        # TODO: make this a context manager?
        sequence = self.get_rendered_filename(sequence)
        if assert_exists:
            assert os.path.exists(sequence)
        return PersistentFramePacker(self.device_collection, sequence)

    def get_meta(self, sequence):
        return self.meta_manager.get_meta(self.sequence_modules.get(sequence, sequence))

    def reload_sequences(self, sequence_files=None):
        """
        Traps for the Unwary in Python’s Import System
          http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html
        """

        def _all_sequence_files():
            return tuple(
                (f.relative, f.abspath)
                for f in fast_scan(str(self.path_sequences), search_filter=FAST_SCAN_REGEX_FILTER_FOR_PY_FILES)
            )

        bar_sequence_name_label = progressbar.FormatCustomText('%(sequence_name)-20s', {'sequence_name': ''})
        bar = progressbar.ProgressBar(
            widgets=(
                'Rendering: ', bar_sequence_name_label, ' ', progressbar.Bar(marker='=', left='[', right=']'),
            ),
        )

        for f_relative, f_absolute in bar(sequence_files or _all_sequence_files()):
            bar_sequence_name_label.update_mapping(sequence_name=f_relative)
            self._render_sequence_module(
                self._load_sequence_module(f_relative),
            )

    def _load_sequence_module(self, f_relative):
        f_relative = f_relative.strip('\\')
        package_name = REGEX_PY_EXTENSION.sub('', f_relative).replace('\\', '.').replace('/', '.')
        if package_name in self.sequence_modules:
            importlib.reload(self.sequence_modules[package_name])
        else:
            self.sequence_modules[package_name] = importlib.import_module(f'{self.path_sequences.stem}.{package_name}')
        sequence_module = self.sequence_modules[package_name]
        setattr(sequence_module, '_sequence_name', sequence_module.__name__.replace(f'{sequence_module.__package__}.', ''))
        return sequence_module

    def _render_sequence_module(self, sequence_module):
        """
        A sequence is rendered to 2 files
          1.) a binary representation of the lights, split into frames of lighting rig state
          2.) a json dict of events (with the rendered timings and durations)
        """
        log.debug('Rendering sequence_module {}'.format(sequence_module._sequence_name))

        packer = self.get_packer(sequence_module, assert_exists=False)
        timeline, triggerline = render_sequence(
            packer=packer,
            sequence_module=sequence_module,
            device_collection=self.device_collection,
            get_time_func=self.meta_manager.get_meta(sequence_module)['get_time_func'],
            get_media_duration_func=self.get_media_duration_func,
            frame_rate=self.framerate,  # TODO: correct inconsistent naming
        )
        packer.close()
        assert os.path.exists(packer.filename), f'Should have generated sequence file {packer.filename}'

        with open(self.get_rendered_trigger_filename(sequence_module), 'wt') as filehandle:
            json.dump(triggerline.data, filehandle)
