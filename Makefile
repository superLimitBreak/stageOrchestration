OS = $(shell uname -s)

help:
	@printf "To install run 'make install'\n"

install: $(OS)

Linux:
	@printf "Linux Install\n"
	@printf "=============\n\n"

	@if dpkg -s ola ola-python >> /dev/null 2> /dev/null ; then \
		printf "	OLA and Python API already installed\n"; \
	else \
		@printf "Installing OLA and Python APIs\n" ; \
		sudo sh -c "apt-get update && apt-get install ola ola-python -y" ; \
	fi

Darwin:
	@printf "OSX Install\n"
	@printf "===========\n\n"
	
	@if python -c "import ola" >> /dev/null 2> /dev/null ; then \
		printf "	OLA and Python API already installed\n"; \
	else \
		@printf "Installing OLA and Python APIs\n" ; \
		# 'protobuf' needs to be installed at the system level python as this is used to build OLA's python libs
		pip2 install protobuf ; \
		brew install ola --with-python ; \
	fi
	# Pygame install notes for python2
	#brew tap Homebrew/python
	#brew update
	#brew install pygame
	#
	#brew install python sdl sdl_image sdl_mixer sdl_ttf portmidi mercurial
	#pip2 install hg+http://bitbucket.org/pygame/pygame

udp.py:
	curl https://raw.githubusercontent.com/calaldees/libs/master/python3/lib/net/upd.py --compressed -O


run: install env setup
	env/bin/python main.py

setup:
	ola_patch -d 1 -p 0 -u 0

env:
	virtualenv -p /usr/bin/python2.7 env
	cp -r /usr/lib/python2.7/dist-packages/ola env/lib/python2.7
	cp -r /usr/lib/python2.7/dist-packages/google env/lib/python2.7/
