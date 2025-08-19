.PHONY: test lint clean

# Run tests using the reproducible script (creates .venv_ci)
test:
	./scripts/run-tests.sh

# Run lint and static checks
lint:
	# Fast lint with ruff and type check with mypy
	python3 -m pip install --upgrade pip
	pip install ruff mypy
	python3 -m ruff check src/
	python3 -m mypy src/ --ignore-missing-imports

clean:
	rm -rf .venv_ci
