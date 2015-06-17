from libs.pygame_midi_input import MidiInput

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererMidiInput(AbstractDMXRenderer):
    CONTROL_OFFSET_JUMP = 8

    def __init__(self, name):
        super().__init__()

        self.midi_input = MidiInput(name)
        self.midi_input.init_pygame()
        self.midi_input.midi_event = self.midi_event  # Dynamic POWER!!!! Remap the midi event to be on this object!

        self._control_offset = 0

    def render(self, frame):
        self.midi_input.process_events()
        return self.dmx_universe

    def midi_event(self, event, data1, data2, data3):
        if data1 == 46:
            self.loop.running = False
        if data1 == 59 and data2 == 127:
            self.control_offset += self.CONTROL_OFFSET_JUMP
            log.info('control_offset: {0}'.format(self.control_offset))
        if data1 == 58 and data2 == 127:
            self.control_offset += -self.CONTROL_OFFSET_JUMP
            log.info('control_offset: {0}'.format(self.control_offset))
        if data1 >= 0 and data1 < self.CONTROL_OFFSET_JUMP:
            self.dmx_universe[self.control_offset + data1] = data2 * 2
        #print('lights2 {0} {1} {2} {3}'.format(event, data1, data2, data3))

    def close(self):
        self.midi_input.close()

    @property
    def control_offset(self):
        return self._control_offset
    @control_offset.setter
    def control_offset(self, value):
        self._control_offset = min((max(0, int(value))), min(512, len(self.dmx_universe) - self.CONTROL_OFFSET_JUMP))
