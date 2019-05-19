ENV=_env
PYTHON_VERSION:=3
DEPENDENCIES_PYTHON:=requirements.pip
PYTHON:=$(ENV)/bin/python$(PYTHON_VERSION)
PIP:=$(ENV)/bin/pip$(PYTHON_VERSION)
PYTEST:=$(ENV)/bin/py.test

CONFIG_DEVELOPMENT=config.development.yaml
CONFIG_PRODUCTION=config.production.yaml
CONFIG_DIST=config.dist.yaml

help:
	#
	# stageOrchestration - Triggerable timed stage lighting + projector orchistration
	#  - install                :
	#    - upgrade_pip          : Update python dependencys
	#  - run                    : Run in development mode
	#    - run_production       : Braudcast to Artnet3
	#  - test                   : Run unit tests
	#


# Install ----------------------------------------------------------------------

.PHONY: install dependencys
dependencys: $(ENV)
install: dependencys upgrade_pip test

$(ENV):
	virtualenv --no-site-packages -p python$(PYTHON_VERSION) $(ENV)

$(CONFIG_DEVELOPMENT):
	cp $(CONFIG_DIST) $@
#$(CONFIG_PRODUCTION):
#	cp $(CONFIG_DIST) $@

.PHONY: link_local_libs
link_local_libs: $(ENV)
	# Local link of 'calaldees' python libs
	$(PIP) install -e ../libs/


# Python Dependencys -----------------------------------------------------------

.PHONY: upgrade_pip
upgrade_pip:
	$(PIP) install --upgrade pip ; $(PIP) install --upgrade -r $(DEPENDENCIES_PYTHON)


# Run --------------------------------------------------------------------------

.PHONY: run run_production

run: $(CONFIG_DEVELOPMENT)
	$(PYTHON) server.py --config $(CONFIG_DEVELOPMENT)

run_production: $(CONFIG_PRODUCTION)
	$(PYTHON) server.py --config $(CONFIG_PRODUCTION)


# Tests ------------------------------------------------------------------------

.PHONY: test
test:
	$(PYTEST) --doctest-modules

.PHONY: cloc
cloc:
	cloc --exclude-dir=$(ENV) ./


# Clean ------------------------------------------------------------------------

clean_cache:
	find . -iname *.pyc -delete
	find . -iname __pycache__ -delete
	find . -iname .cache -delete

clean: clean_cache
	rm -rf $(ENV)
	#rm -rf $(CONFIG_DEVELOPMENT)
