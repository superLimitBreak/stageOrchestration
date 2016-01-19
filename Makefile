
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
	if [ -d ../../libs/ ] ; then \
		ln -s ../../libs/python3/lib/misc.py misc.py ;\
		ln -s ../../libs/python3/lib/loop.py loop.py ;\
		ln -s ../../libs/python3/lib/net/udp.py udp.py ;\
		ln -s ../../libs/python3/lib/net/client_reconnect.py client_reconnect.py ;\
		ln -s ../../libs/python3/lib/midi/pygame_midi_wrapper.py pygame_midi_wrapper.py ;\
		ln -s ../../libs/python3/lib/midi/pygame_midi_input.py pygame_midi_input.py ;\
		ln -s ../../libs/python3/lib/midi/music.py music.py ;\
		ln -s ../../libs/python3/lib/pygame_helpers/pygame_base.py pygame_base.py ;\
	else \
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/misc.py;\
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/loop.py;\
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/net/udp.py;\
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/net/client_reconnect.py;\
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/pygame_midi_wrapper.py;\
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/pygame_midi_input.py;\
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/music.py;\
		wget -cq https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/pygame/pygame_base.py;\
	fi

# PentatonicHero plugin --------------------------------------------------------

PENTATONIC_HERO_SOURCE_FILE=PentatonicHero/DMXRendererPentatonicHero.py
PENTATONIC_HERO_DESTINATION_FILE=./lighting/renderers/PentatonicHero.py
lighting/renderers/PentatonicHero.py:
	if [ -d ../PentatonicHero/ ] ; then \
		ln -s ../../../$(PENTATONIC_HERO_SOURCE_FILE) $(PENTATONIC_HERO_DESTINATION_FILE) ;\
	else \
		wget -qc https://raw.githubusercontent.com/SuperLimitBreak/pentatonicHero/master/DMXRendererPentatonicHero.py --output-file=$(PENTATONIC_HERO_DESTINATION_FILE);\
	fi


# Extneral Python lib dependecys -----------------------------------------------

pytweening:
	mkdir pytweening
pytweening/__init__.py: pytweening
	cd pytweening && wget -qc https://raw.githubusercontent.com/asweigart/pytweening/master/pytweening/__init__.py



# Run --------------------------------------------------------------------------

.PHONY: run run_midi_input run_production run_simulator run_simulator2

run:
	python3 lightingAutomation.py --postmortem

run_midiRemote:
	python3 midiRemoteControl.py 'nanoKONTROL2' --postmortem

run_production:
	python3 lightingAutomation.py --artnet_dmx_host 192.168.0.111

run_simulator:
	# To be replaced by simulator2
	python3 simulator.py

run_simulator2:
	python3 simulator2.py


# Clean ------------------------------------------------------------------------

clean:
	rm -rf libs
	rm -rf pytweening
	rm -rf $(PENTATONIC_HERO_DESTINATION_FILE)
