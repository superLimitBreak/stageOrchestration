OS = $(shell uname -s)

help:
	@printf "To install run 'make install'\n"


# Install ----------------------------------------------------------------------

install: python_libs pytweening/__init__.py

install_plugin_pentetonic_hero:
	curl https://raw.githubusercontent.com/calaldees/PentatonicHero/DMXRendererPentatonicHero.py --compressed -O


# Extneral Python lib dependecys -----------------------------------------------

pytweening:
	mkdir pytweening
pytweening/__init__.py: pytweening
	cd pytweening && curl https://raw.githubusercontent.com/asweigart/pytweening/master/pytweening/__init__.py --compressed -O


# Custom Python Dependencys ----------------------------------------------------

python_libs: libs/udp.py libs/pygame_midi_wrapper.py libs/pygame_midi_input.py libs/music.py libs/loop.py libs/misc.py libs/network_display_event.py
libs:
	mkdir libs
	touch libs/__init__.py
libs/misc.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/misc.py --compressed -O
libs/loop.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/loop.py --compressed -O
libs/udp.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/net/upd.py --compressed -O
libs/network_display_event.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/net/network_display_event.py --compressed -O
libs/pygame_midi_wrapper.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/pygame_midi_wrapper.py --compressed -O
libs/pygame_midi_input.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/pygame_midi_input.py --compressed -O
libs/music.py: libs
	cd libs && curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/midi/music.py --compressed -O

python_libs_local_link: libs
	# Link local libs; use when all the required repos are checked out locally
	ln -s ../libs/python3/lib/misc.py ./libs/misc.py
	ln -s ../libs/python3/lib/oop.py ./libs/loop.py
	ln -s ../libs/python3/lib/net/upd.py ./libs/upd.py
	ln -s ../libs/python3/lib/net/network_display_event.py ./libs/network_display_event.py
	ln -s ../libs/python3/lib/midi/pygame_midi_wrapper.py ./libs/pygame_midi_wrapper.py
	ln -s ../libs/python3/lib/midi/pygame_midi_input.py ./libs/pygame_midi_input.py
	ln -s ../PentatonicHero/DMXRendererPentatonicHero.py ./DMXRendererPentatonicHero.py


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
