
#from pygame_midi_wrapper import PygameMidiDeviceHelper
#pygame.midi.init()
#devices = PygameMidiDeviceHelper.get_devices()
#print([m for m in devices])
#import pdb ; pdb.set_trace()
#midi_in = PygameMidiDeviceHelper.open_device('nanoKONTROL2 CTRL', io='input')

from pygame_midi_input import MidiInputPlugin


class LightingControl(MidiInputPlugin):

    def __init__(self):
        super().__init__('nanoKONTROL2')
        self.open()

    def midi_event(self, event, data1, data2, data3):
        #log.debug(event)
        print('{0} {1} {2} {3}'.format(event, data1, data2, data3))

def postmortem(func):
    import traceback
    import pdb
    import sys
    try:
        func()
    except:
        type, value, tb = sys.exc_info()
        traceback.print_exc()
        pdb.post_mortem(tb)

postmortem(LightingControl)