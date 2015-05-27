from pygame_midi_input import MidiInput


class LightingControl(MidiInput):

    def __init__(self):
        super().__init__('nanoKONTROL2')
        self.open()

    def midi_event(self, event, data1, data2, data3):
        #log.debug(event)
        print('{0} {1} {2} {3}'.format(event, data1, data2, data3))


LightingControl()