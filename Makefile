ENV=_env
PYTHON=$(ENV)/bin/python3
PIP=$(ENV)/bin/pip3
PYTEST=$(ENV)/bin/py.test

EXT=ext
EXT_SOURCE_URL=https://raw.githubusercontent.com/calaldees/libs/master/python3/lib
EXT_LOCAL_PATH=../../libs/python3/lib

CONFIG_DEVELOPMENT=config.development.yaml
CONFIG_PRODUCTION=config.production.yaml
CONDIG_DIST=config.dist.yaml

help:
	#
	# stageOrchestration - Triggerable timed stage lighting + projector orchistration
	#  - install                :
	#    - upgrade_pip          : Update python dependencys
	#  - run                    : Run in development mode
	#    - run_production       : Braudcast to Artnet3
	#  - test                   :
	#


# Install ----------------------------------------------------------------------

.PHONY: install dependencys
dependencys: $(ENV) $(EXT)
install: dependencys upgrade_pip test

$(ENV):
	virtualenv -p python3 $(ENV)

#$(CONFIG_DEVELOPMENT):
#	cp $(CONFIG_DIST) $@
#$(CONFIG_PRODUCTION):
#	cp $(CONFIG_DIST) $@



# Python Dependencys -----------------------------------------------------------

$(EXT):
	mkdir $(EXT)
	touch $(EXT)/__init__.py
	cd $(EXT) && \
	if [ -d $(EXT_LOCAL_PATH)/ ] ; then \
		ln -s $(EXT_LOCAL_PATH)/misc.py misc.py ;\
		ln -s $(EXT_LOCAL_PATH)/loop.py loop.py ;\
		ln -s $(EXT_LOCAL_PATH)/attribute_packer.py attribute_packer.py ;\
		ln -s $(EXT_LOCAL_PATH)/net/udp.py udp.py ;\
		ln -s $(EXT_LOCAL_PATH)/net/http_dispatch.py http_dispatch.py ;\
		ln -s $(EXT_LOCAL_PATH)/net/client_reconnect.py client_reconnect.py ;\
		ln -s $(EXT_LOCAL_PATH)/midi/music.py music.py ;\
		ln -s $(EXT_LOCAL_PATH)/animation/timeline.py timeline.py ;\
	else \
		wget -cq $(LIB_URL)/misc.py ;\
		wget -cq $(LIB_URL)/loop.py ;\
		wget -cq $(LIB_URL)/attribute_packer.py ;\
		wget -cq $(LIB_URL)/net/udp.py ;\
		wget -cq $(LIB_URL)/net/http_dispatch.py ;\
		wget -cq $(LIB_URL)/net/client_reconnect.py ;\
		wget -cq $(LIB_URL)/midi/music.py ;\
		wget -cq $(LIB_URL)/animation/timeline.py ;\
	fi

.PHONY: upgrade_pip
upgrade_pip:
	$(PIP) install --upgrade pip ; $(PIP) install --upgrade -r dependencys.pip


# Run --------------------------------------------------------------------------

.PHONY: run run_production

run: $(CONFIG_DEVELOPMENT)
	$(PYTHON) server.py --config $(CONFIG_DEVELOPMENT)

run_production: $(CONFIG_PRODUCTION)
	$(PYTHON) server.py --config $(CONFIG_PRODUCTION)


# Tests ------------------------------------------------------------------------

.PHONY: test
test:
	PYTHONPATH=./ $(PYTEST) $(EXT) stageOrchestration tests --doctest-modules --pdb -x

.PHONY: cloc
cloc:
	cloc --exclude-dir=$(ENV),$(EXT) ./


# Clean ------------------------------------------------------------------------

clean:
	find . -iname *.pyc -delete
	find . -iname __pycache__ -delete
	find . -iname .cache -delete
	rm -rf $(ENV)
	rm -rf $(EXT)
	#rm -rf $(CONFIG)
