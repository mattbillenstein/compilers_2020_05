PYTHON_FILES = $(shell fd .py$$ exercises)

all: format lint type-check test

format:
	@black --quiet --line-length 99 $(PYTHON_FILES)

lint:
	@flake8 $(PYTHON_FILES)

type-check:
	@mypy --check-untyped-defs --config-file=tox.ini $(PYTHON_FILES)

test:
	@for f in exercises/warmup/*.py; do \
		python $$f; \
	done
	@python -m doctest $(PYTHON_FILES)

.PHONY: format lint type-check test
