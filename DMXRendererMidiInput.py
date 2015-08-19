from colorsys import hsv_to_rgb

from libs.pygame_midi_input import MidiInput

from DMXBase import AbstractDMXRenderer

import logging
log = logging.getLogger(__name__)


class DMXRendererMidiInput(AbstractDMXRenderer):
    """
    Take midi input from the Korg USB nanoKONTROL2 and control the lighting rig in realtime.

    This is intended to be a debug test system.

    To support other controlers/lighting system the magic number of the
    midi address's and lighting address's will need changing manually.

    Sliders control a single lights red,green,blue,white,control directly.
    Nobs manipulate groups of lights using HSV
    """

    CONTROL_OFFSET_JUMP = 8
    CONTROL_ID_HSV_A = 16
    CONTROL_ID_HSV_B = 20
    HSV_A_INDEXS = [8, 16, 24, 32, 40, 48]
    HSV_B_INDEXS = [0, 56]

    def __init__(self, name):
        super().__init__()

        self.midi_input = MidiInput(name)
        self.midi_input.init_pygame()
        self.midi_input.midi_event = self.midi_event  # Dynamic POWER!!!! Remap the midi event to be on this object!

        self._control_offset = 0
        self.hsv_a = [0.0, 0.0, 0.0, 0.0]
        self.hsv_b = [0.0, 0.0, 0.0, 0.0]

    def render(self, frame):
        self.midi_input.process_events()  # Poll the midi input per frame (This prevents the need for another thread to monitor the midi state)
        return self.dmx_universe

    def midi_event(self, event, data1, data2, data3):
        if data1 == 46:
            #self.loop.running = False
            print('Exit is disbaled, bloody well fix it')
        if data1 == 59 and data2 == 127:
            self.control_offset += self.CONTROL_OFFSET_JUMP
            log.info('control_offset: {0}'.format(self.control_offset))
        if data1 == 58 and data2 == 127:
            self.control_offset += -self.CONTROL_OFFSET_JUMP
            log.info('control_offset: {0}'.format(self.control_offset))
        if data1 >= 0 and data1 < self.CONTROL_OFFSET_JUMP:
            self.dmx_universe[self.control_offset + data1] = data2 * 2
            #print('single:', self.control_offset + data1, self.dmx_universe[self.control_offset + data1])

        def color_float_to_byte(value):
            return min(255, max(0, int(value * 255)))
        def render_hsv_from_state(indexs, color):
            for dmx_index in indexs:
                for color_index, color_component in enumerate(list(hsv_to_rgb(*color[:3])) + color[3:4]):
                    self.dmx_universe[dmx_index + color_index] = color_float_to_byte(color_component)
        def update_hsv_from_input(control_id, value, id_range, hsv_color):
            if control_id in range(id_range, id_range + 4):
                hsv_color[control_id - id_range] = value / 127
                return True
        if update_hsv_from_input(data1, data2, self.CONTROL_ID_HSV_A, self.hsv_a):
            render_hsv_from_state(self.HSV_A_INDEXS, self.hsv_a)
        if update_hsv_from_input(data1, data2, self.CONTROL_ID_HSV_B, self.hsv_b):
            render_hsv_from_state(self.HSV_B_INDEXS, self.hsv_b)

    def close(self):
        self.midi_input.close()

    @property
    def control_offset(self):
        return self._control_offset
    @control_offset.setter
    def control_offset(self, value):
        self._control_offset = min((max(0, int(value))), min(512, len(self.dmx_universe) - self.CONTROL_OFFSET_JUMP))
