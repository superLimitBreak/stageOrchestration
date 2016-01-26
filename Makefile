ENV = _env
PYTHON = $(ENV)/bin/python3
PIP = $(ENV)/bin/pip3

help:
	# Automated ArtNet3 DMX Lighting System
	#  - install        		: Install dependencies
	#  - install_development 	: Install optional dependenciees for development
	#  - run            		:
	#  - run_production 		: Drive a remote ArtNet3 server
	#  - run_midiRemote 		: Use local midi device ()with pygame) to control a remote lightingAutomation instance
	#  - run_simulator  		: Pygame based visulisation of ArtNet packets
	# Requires python3 + pyyaml lib + [optional pygame for local midi control]


# Install ----------------------------------------------------------------------

.PHONY: install
install: $(ENV) libs lighting/renderers/PentatonicHero.py requirements

.PHONY: install_development
install_development: pygame

$(ENV):
	virtualenv -p python3 $(ENV)

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

# This kind of stuff would make most sense in a setup.py
.PHONY: requirements
requirements:
	$(PIP) install --upgrade pip ; $(PIP) install --upgrade -r requirements.pip

.Phony: pygame
pygame:
	# There is no python3-pygame package - The Pygame wiki suggests compileing it yourself.
	# http://www.pygame.org/wiki/CompileUbuntu
	if [ $$($(PIP) list | grep -c pygame) -eq 0 ];\
		then\
		echo "Installing pygame";\
		$(PIP) install hg+http://bitbucket.org/pygame/pygame;\
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



# Run --------------------------------------------------------------------------

.PHONY: run run_midi_input run_production run_simulator run_simulator2

run:
	$(PYTHON) lightingAutomation.py --postmortem

run_midiRemote:
	$(PYTHON) midiRemoteControl.py 'nanoKONTROL2' --postmortem

run_production:
	$(PYTHON) lightingAutomation.py --artnet_dmx_host 192.168.0.111

run_simulator:
	$(PYTHON) simulator.py


# Clean ------------------------------------------------------------------------

clean:
	rm -rf $(ENV)
	rm -rf libs
	rm -rf $(PENTATONIC_HERO_DESTINATION_FILE)
