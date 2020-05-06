BIN = ~/tmp/virtualenvs/compilers/bin
PYTHON = $(BIN)/python
BLACK = $(BIN)/black
FLAKE8 = $(BIN)/flake8
MYPY = $(BIN)/mypy
PYTEST = $(BIN)/pytest
PYTHON_FILES = wabbit/model.py script_models.py

all: lint type-check test wabbitscript-examples

format:
	@$(BIN) --quiet --line-length 99 $(PYTHON_FILES)

lint:
	@$(FLAKE8) $(PYTHON_FILES)

type-check:
	@$(MYPY) --check-untyped-defs --config-file=tox.ini --no-color-output $(PYTHON_FILES)

test:
	$(PYTEST) --quiet wabbit/tokenize.py

test-python-exercises:
	@$(PYTHON) -m doctest $(PYTHON_FILES)
	@for f in exercises/python/warmup/*.py; do \
		$(PYTHON) $$f; \
	done

wabbitscript-examples:
	$(PYTHON) script_models.py

ELISP_FILES = $(shell fd .el$$ exercises)
test-elisp:
	@for f in $(ELISP_FILES); do \
		emacs -batch -l $$f -f ert-run-tests-batch-and-exit; \
	done

.PHONY: format lint type-check test-python test-elisp test
