
help:
	# Automated ArtNet3 DMX Lighting System
	#  - install        : Install dependencys
	#  - run            :
	#  - run_production : Drive a remote ArtNet3 server
	#  - run_midiRemote : Use local midi device ()with pygame) to control a remote lightingAutomation instance
	#  - run_simulator  : Pygame based visulisation of ArtNet packets
	# Requires python3 + pyyaml lib + [optional pygame for local midi control]


# Install ----------------------------------------------------------------------

.PHONY: install
install: libs pytweening/__init__.py lighting/renderers/PentatonicHero.py



# Python Dependencys -----------------------------------------------------------

libs:
	mkdir libs
	touch libs/__init__.py
	cd libs && \
	if [ -d ../libs/ ] ; then \
		ln -s ../../libs/python3/lib/misc.py misc.py ;\
		ln -s ../../libs/python3/lib/loop.py loop.py ;\
		ln -s ../../libs/python3/lib/net/udp.py udp.py ;\
		ln -s ../../libs/python3/lib/net/client_reconnect.py client_reconnect.py ;\
		ln -s ../../libs/python3/lib/midi/pygame_midi_wrapper.py pygame_midi_wrapper.py ;\
		ln -s ../../libs/python3/lib/midi/pygame_midi_input.py pygame_midi_input.py ;\
		ln -s ../../libs/python3/lib/midi/music.py music.py ;\
	else \
		curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/misc.py                      --compressed -O ;\
		curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/loop.py                      --compressed -O ;\
		curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/net/udp.py                   --compressed -O ;\
		curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/net/client_reconnect.py      --compressed -O ;\
		curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/pygame_midi_wrapper.py  --compressed -O ;\
		curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/pygame_midi_input.py    --compressed -O ;\
		curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/music.py                --compressed -O ;\
	fi

# PentatonicHero plugin --------------------------------------------------------

PENTATONIC_HERO_SOURCE_FILE=PentatonicHero/DMXRendererPentatonicHero.py
PENTATONIC_HERO_DESTINATION_FILE=./lighting/renderers/PentatonicHero.py
lighting/renderers/PentatonicHero.py:
	if [ -d ../PentatonicHero/ ] ; then \
		ln -s ../../../$(PENTATONIC_HERO_SOURCE_FILE) $(PENTATONIC_HERO_DESTINATION_FILE) ;\
	else \
		curl https://raw.githubusercontent.com/calaldees/$(PENTATONIC_HERO_SOURCE_FILE) --compressed -o $(PENTATONIC_HERO_DESTINATION_FILE) ;\
	fi


# Extneral Python lib dependecys -----------------------------------------------

pytweening:
	mkdir pytweening
pytweening/__init__.py: pytweening
	cd pytweening && curl https://raw.githubusercontent.com/asweigart/pytweening/master/pytweening/__init__.py --compressed -O



# Run --------------------------------------------------------------------------

.PHONY: run run_midi_input run_production run_simulator

run:
	python3 lightingAutomation.py --postmortem

run_midiRemote:
	python3 midiRemoteControl.py 'nanoKONTROL2' --postmortem

run_production:
	python3 lightingAutomation.py --artnet_dmx_host 192.168.0.111

run_simulator:
	python3 simulator.py


# Clean ------------------------------------------------------------------------

clean:
	rm -rf libs
	rm -rf pytweening
	rm -rf $(PENTATONIC_HERO_DESTINATION_FILE)
