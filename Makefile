BIN = ~/tmp/virtualenvs/compilers/bin
PYTHON = $(BIN)/python
BLACK = $(BIN)/black
FLAKE8 = $(BIN)/flake8
MYPY = $(BIN)/mypy
PYTEST = $(BIN)/pytest
PYTHON_FILES = wabbit/c.py wabbit/model.py wabbit/tokenize.py wabbit/typecheck.py wabbit/parse.py wabbit/interp.py script_models.py
WABBITSCRIPT_FILES = tests/Script/*.wb

all: lint type-check test

format:
	@$(BIN) --quiet --line-length 99 $(PYTHON_FILES)

lint:
	@$(FLAKE8) $(PYTHON_FILES)

type-check:
	@$(MYPY) --check-untyped-defs --no-warn-no-return --config-file=tox.ini --no-color-output $(PYTHON_FILES)

test:
	$(PYTEST) --quiet wabbit/tokenize.py
	$(PYTEST) --quiet tests/interp.py

test-python-exercises:
	@$(PYTHON) -m doctest $(PYTHON_FILES)
	@for f in exercises/python/warmup/*.py; do \
		$(PYTHON) $$f; \
	done

wabbitscript-examples:
	@$(PYTHON) script_models.py
	@for f in $(WABBITSCRIPT_FILES); do \
		$(PYTHON) -m wabbit.tokenize $$f > /dev/null; \
	done

parse:
	@for f in $(WABBITSCRIPT_FILES); do \
		$(PYTHON) -m wabbit.parse $$f; \
	done

ELISP_FILES = $(shell fd .el$$ exercises)
test-elisp:
	@for f in $(ELISP_FILES); do \
		emacs -batch -l $$f -f ert-run-tests-batch-and-exit; \
	done

.PHONY: all format lint type-check test test-python-exercises wabbitscript-examples test-elisp
