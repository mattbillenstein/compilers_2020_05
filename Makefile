ELISP_FILES = $(shell fd .el$$ exercises)
PYTHON_FILES = $(shell fd .py$$ exercises)

all: format lint type-check test

format:
	@black --quiet --line-length 99 $(PYTHON_FILES)

lint:
	@flake8 $(PYTHON_FILES)

type-check:
	@mypy --check-untyped-defs --config-file=tox.ini $(PYTHON_FILES)

test: test-python test-elisp

test-python:
	@for f in exercises/warmup/*.py; do \
		python $$f; \
	done
	@python -m doctest $(PYTHON_FILES)

test-elisp:
	@for f in $(ELISP_FILES); do \
		emacs -batch -l $$f -f ert-run-tests-batch-and-exit; \
	done

.PHONY: format lint type-check test-python test-elisp test
