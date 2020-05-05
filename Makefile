PYTHON = ~/tmp/virtualenvs/compilers/bin/python
PYTHON_FILES = wabbit/model.py script_models.py

all: format lint type-check test

format:
	@black --quiet --line-length 99 $(PYTHON_FILES)

lint:
	@flake8 $(PYTHON_FILES)

type-check:
	@mypy --check-untyped-defs --config-file=tox.ini $(PYTHON_FILES)

test: test-python

test-python:
	@$(PYTHON) -m doctest $(PYTHON_FILES)

test-python-exercises:
	@for f in exercises/python/warmup/*.py; do \
		$(PYTHON) $$f; \
	done

ELISP_FILES = $(shell fd .el$$ exercises)
test-elisp:
	@for f in $(ELISP_FILES); do \
		emacs -batch -l $$f -f ert-run-tests-batch-and-exit; \
	done

.PHONY: format lint type-check test-python test-elisp test
