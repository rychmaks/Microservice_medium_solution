#
# Makefile for rfadjustments
#
DOCKER_REGISTRY?=192.168.240.173:50444

PIP_TRUSTED_HOST?=192.168.240.173
PIP_INDEX_URL?=http://192.168.240.173:50081/repository/pypi/pypi
PIP_EXTRA_INDEX_URL?=http://192.168.240.173:50081/repository/pypi/simple

export PATH:=virtualenv/bin:venv/bin:$(PATH)

.PHONY: help
help:
	@echo 'Makefile for BU Sanic playground'
	@echo ''
	@echo '1. Building:'
	@echo '  make setup         (re)Build your environment and setup project'
	@echo ''
	@echo '2. Testing:'
	@echo '  make test          Run tests and check code with flake8'
	@echo '  make flake         Check code with flake8'
	@echo ''
	@echo '3. Formatting:'
	@echo '  make format       Format code according to PEP 8 rules'
	@echo ''
	@echo '4. Type check:'
	@echo '  make check-types       Check types by type hints'
	@echo ''
	@echo '5. Running:'
	@echo '  make run-dev       Run locally using dev server'
	@echo ''
	@echo '6. Compile versions:'
	@echo '  make compile-versions    Pin versions of newly added dependencies'
	@echo ''

.PHONY: setup_venv
setup_venv: clean
	@echo ' -- Setting up environment'
	sudo pip3 install --upgrade pip pip-tools virtualenv
	virtualenv -p python3.7 --always-copy --system-site-packages venv
	venv/bin/pip install -e .'[dev,test]' --extra-index-url $(PIP_EXTRA_INDEX_URL) --index-url $(PIP_INDEX_URL) --trusted-host $(PIP_TRUSTED_HOST)
	mkdir -pv .git/hooks/
	cp pre-commit .git/hooks/
	@printf ' -- Environment is ready.\n Activation command: `source venv/bin/activate`\n'

.PHONY: setup
setup:
	@echo ' -- Installing dependencies'
	sudo apt-get -y install python3-dev python3-pip libpq-dev supervisor shellcheck
	make setup_venv

.PHONY: setup_mac
setup_mac:
	@echo ' -- Installing dependencies'
	brew update && brew install git python pkg-config shellcheck
	make setup_venv

.PHONY: clean clean-config
clean: clean-files clean-config

clean-files:
	@rm -rf venv/
	@rm -rf *.egg-info

clean-config:
	rm -fv configure config.log config.status
	git checkout Dockerfile
	rm -fr autom4te.cache

.PHONY: flake
flake:
	flake8

.PHONY: format
format:
	black --line-length=120 $$(find service_api -name '*.py')

.PHONY: check-types
check-types:
	pyre --source-directory service_api --search-path . check

.PHONY: check
check: check-types flake

.PHONY: test
test: flake
	py.test tests

.PHONY: coverage
coverage: flake
	coverage run --rcfile=.coveragerc venv/bin/py.test -v tests/
	coverage report --rcfile=.coveragerc

.PHONY: run-dev
run-dev:
	python manage.py runserver

.PHONY: compile-versions
compile-versions:
	pip-compile -v --extra-index-url $(PIP_EXTRA_INDEX_URL) --index-url $(PIP_INDEX_URL) --trusted-host $(PIP_TRUSTED_HOST) --output-file requirements/requirements.txt requirements/requirements.in --no-index --no-emit-trusted-host
	pip-compile -v --extra-index-url $(PIP_EXTRA_INDEX_URL) --index-url $(PIP_INDEX_URL) --trusted-host $(PIP_TRUSTED_HOST) --output-file requirements/test_requirements.txt requirements/test_requirements.in requirements/requirements.txt --no-index --no-emit-trusted-host

.PHONY: configure
configure:
	autoconf
	./configure --with-docker-registry=$(DOCKER_REGISTRY) --with-pip-trusted-host=$(PIP_TRUSTED_HOST) --with-pip-index-url="$(PIP_INDEX_URL)" --with-pip-extra-index-url="$(PIP_EXTRA_INDEX_URL)"

.PHONY: doc-upload
doc-upload:
	$(MAKE) -C docs/ html && \
	python -m msp_docs2confluence.run True

.PHONY: doc
doc:
	$(MAKE) -C docs/ html && \
	python -m msp_docs2confluence.run False

.PHONY: doc-upload-clear
doc-upload-clear:
	$(MAKE) -C docs/ html && \
	python -m msp_docs2confluence.run True
	@rm -rf docs_to_confluence
	@rm -rf docs/build