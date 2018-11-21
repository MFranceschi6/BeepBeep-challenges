HERE = $(shell pwd)
VENV = .
VIRTUALENV = virtualenv
BIN = $(VENV)/bin
PYTHON = $(BIN)/python
API=api.yaml
PKG=beepbeep
SERVICE=challenge-microservice

INSTALL = $(BIN)/pip install --no-deps

.PHONY: all test

all: build

$(PYTHON):
	$(VIRTUALENV) $(VTENV_OPTS) $(VENV)

build: $(PYTHON)
	$(PYTHON) setup.py develop

clean:
	rm -rf $(VENV)

test_dependencies:
	$(BIN)/pip install flake8 tox

test: build test_dependencies
	$(BIN)/tox

run:
	FLASK_APP=dataservice/app.py flask run

doc_dependencies:
	curl -sL https\://deb.nodesource.com/setup_8.x | sudo bash - && apt-get install nodejs bundler && npm install -g widdershins

slate:
	git clone https\://github.com/lord/slate.git

widdershins: slate
	widdershins --expandBody ./$(PKG)/$(SERVICE)/static/$(API) -o ./slate/source/index.html.md

build_middleman: slate
ifeq ($(shell  gem list \^middleman\$$ -i),false)
	cd ./slate && bundle install
endif

build_docs: widdershins build_middleman
	cd ./slate && bundle exec middleman build

create_static_doc:
	mkdir -p $(PKG)/$(SERVICE)/static/doc/

create_docs:
	mkdir -p docs

docs: widdershins build_docs create_static_doc create_docs
	cd ./slate && cp -r build/* ../$(PKG)/$(SERVICE)/static/doc/ && cp -r build/* ../docs/

clean-doc:
	rm  -rf slate
