.PHONY: test lint lint-fix typecheck format ci clean coverage coverage-html

# Run tests using the reproducible script (creates .venv_ci)
test:
	./scripts/run-tests.sh

# Coverage reports (terminal summary)
coverage:
	./scripts/run-tests.sh --cov=src --cov-report=term-missing

# Coverage reports (HTML)
coverage-html:
	./scripts/run-tests.sh --cov=src --cov-report=html

# CI bundle: tests with coverage + ruff + mypy + pylint
ci:
	./scripts/run-tests.sh --cov=src --cov-report=term-missing
	python3 -m pip install --upgrade pip
	pip install ruff mypy pylint
	python3 -m ruff check src/
	python3 -m mypy src/ --ignore-missing-imports --exclude="src/llm/router.py"
	python3 -m pylint src/ --exit-zero

# Run lint and static checks
lint:
	# Fast lint with ruff and type check with mypy
	python3 -m pip install --upgrade pip
	pip install ruff mypy
	python3 -m ruff check src/
	python3 -m mypy src/ --ignore-missing-imports

# Auto-fix lint issues with ruff
lint-fix:
	python3 -m pip install --upgrade pip
	pip install ruff
	ruff check src/ --fix

# Type checking with mypy (with router exclusion)
typecheck:
	python3 -m pip install --upgrade pip
	pip install mypy
	python3 -m mypy src/ --ignore-missing-imports --exclude="src/llm/router.py"

# Auto-format with ruff
format:
	python3 -m pip install --upgrade pip
	pip install ruff
	ruff format src/

clean:
	rm -rf .venv_ci
