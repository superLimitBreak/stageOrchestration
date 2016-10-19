ENV=_env
PYTHON=$(ENV)/bin/python3
PIP=$(ENV)/bin/pip3
PYTEST=$(ENV)/bin/py.test

EXT=ext
EXT_SOURCE_URL=https://raw.githubusercontent.com/calaldees/libs/master/python3/lib
EXT_LOCAL_PATH=../../libs/python3/lib

CONFIG=config.yaml
CONFIG_SOURCE=config.dist.yaml

ARTNET_ADDRESS=192.168.0.111

help:
	#
	# lightingAutomation - Triggerable timed stage lighting + projector orchistration
	#  - install                :
	#    - dependencys          : Update python dependencys
	#  - run                    : Run in development mode
	#    - run_production       : Braudcast to Artnet3:$(ARTNET_ADDRESS)
	#  - test                   :
	#


# Install ----------------------------------------------------------------------

.PHONY: install
install: $(ENV) $(CONFIG) libs dependencys test

$(ENV):
	virtualenv -p python3 $(ENV)

$(CONFIG):
	cp $(CONFIG_SOURCE) $(CONFIG)

# Python Dependencys -----------------------------------------------------------

$(EXT):
	mkdir $(EXT)
	touch $(EXT)/__init__.py
	cd $(EXT) && \
	if [ -d $(LIB_PATH)/ ] ; then \
		ln -s $(LIB_PATH)/misc.py misc.py ;\
		ln -s $(LIB_PATH)/loop.py loop.py ;\
		ln -s $(LIB_PATH)/net/udp.py udp.py ;\
		ln -s $(LIB_PATH)/net/client_reconnect.py client_reconnect.py ;\
		ln -s $(LIB_PATH)/midi/music.py music.py ;\
	else \
		wget -cq $(LIB_URL)/misc.py ;\
		wget -cq $(LIB_URL)/loop.py ;\
		wget -cq $(LIB_URL)/net/udp.py ;\
		wget -cq $(LIB_URL)/net/client_reconnect.py ;\
		wget -cq $(LIB_URL)/midi/music.py ;\
	fi

.PHONY: dependencys
dependencys:
	$(PIP) install --upgrade pip ; $(PIP) install --upgrade -r dependencys.pip


# Run --------------------------------------------------------------------------

.PHONY: run run_production

run:
	$(PYTHON) lightingAutomation.py --postmortem

run_production:
	$(PYTHON) lightingAutomation.py --yamlscaninterval 0 --artnet_dmx_host $(ARTNET_ADDRESS)


# Tests ------------------------------------------------------------------------

.PHONY: test
test:
	PYTHONPATH=./ $(PYTEST) libs lighting tests --doctest-modules --pdb --maxfail=3

.PHONY: cloc
cloc:
	cloc --exclude-dir=$(ENV),libs ./


# Clean ------------------------------------------------------------------------

clean:
	rm -rf $(ENV)
	rm -rf $(EXT)
	rm -rf $(CONFIG)
