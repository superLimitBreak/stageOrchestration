OS = $(shell uname -s)

help:
	@printf "To install run 'make install'\n"

install: $(OS)

Linux:
	@printf "Linux Install\n"
	@printf "=============\n\n"

	@printf "Installing OLA and Python APIs\n"
	@if dpkg -s ola ola-python >> /dev/null 2> /dev/null ; then \
		printf "	OLA and Python API already installed\n"; \
	else \
		sudo sh -c "apt-get update && apt-get install ola ola-python -y" ; \
	fi

Darwin:
	#Not done

run: install setup
	python main.py

setup:
	ola_patch -d 1 -p 0 -u 0
