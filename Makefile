OS = $(shell uname -s)

help:
	@printf "To install run 'make install'\n"


# Install ----------------------------------------------------------------------

install: libs pytweening/__init__.py DMXRendererPentatonicHero.py



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

DMXRendererPentatonicHero.py:
	if [ -d ../PentatonicHero/ ] ; then \
		ln -s ../PentatonicHero/DMXRendererPentatonicHero.py ./DMXRendererPentatonicHero.py ;\
	else \
		curl https://raw.githubusercontent.com/calaldees/PentatonicHero/DMXRendererPentatonicHero.py --compressed -O ;\
	fi


# Extneral Python lib dependecys -----------------------------------------------

pytweening:
	mkdir pytweening
pytweening/__init__.py: pytweening
	cd pytweening && curl https://raw.githubusercontent.com/asweigart/pytweening/master/pytweening/__init__.py --compressed -O



# Run --------------------------------------------------------------------------

run: python_libs
	python3 DMXManager.py

run_midi_input:
	python3 DMXManager.py --midi_input 'nanoKONTROL2'

run_dmxking:
	python3 DMXManager.py --midi_input 'nanoKONTROL2' --artnet_dmx_host 192.168.0.111

run_simulator: python_libs
	python3 DMXSimulator.py


# Clean ------------------------------------------------------------------------

clean:
	rm -rf libs
	rm -rf pytweening
	rm -rf DMXRendererPentatonicHero.py
