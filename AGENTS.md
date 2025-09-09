# Instructions for AI Agents

This document provides instructions and guidelines for AI agents working with the SDLC_core repository.

## Repository Overview

SDLC_core is a Python-based Software Development Life Cycle core project that provides AI/ML capabilities for software development workflows. The repository contains modules for LLM clients, intelligent agents, memory management, prompt engineering, document retrieval, skill execution, and various utilities.

- **Primary Language**: Python 3.10-3.12
- **Secondary Languages**: TypeScript (for Azure pipelines), Shell scripts
- **Project Type**: AI/ML library and tooling for SDLC workflows

## Environment Setup

### 1. Install Dependencies

**IMPORTANT**: The project's dependencies are split into multiple files. For development and testing, you should install the dependencies from `requirements-dev.txt`.

```bash
pip install -r requirements-dev.txt
```

### 2. Set Python Path

You must set the `PYTHONPATH` to the root of the repository for imports to work correctly.

```bash
export PYTHONPATH=.
```

Alternatively, you can prefix your commands with `PYTHONPATH=.`:

```bash
PYTHONPATH=. python -m pytest
```

## Building and Testing

### Testing

The test infrastructure is set up. Use the following commands to run tests:

```bash
# Run all tests
PYTHONPATH=. python -m pytest test/ -v

# Run tests with coverage
PYTHONPATH=. python -m pytest test/ --cov=src/ --cov-report=xml

# Run specific test suites
PYTHONPATH=. python -m pytest test/unit/ -v
PYTHONPATH=. python -m pytest test/integration/ -v
PYTHONPATH=. python -m pytest test/e2e/ -v
```

### Linting and Static Analysis

```bash
# Run pylint
python -m pylint src/ --exit-zero

# Run mypy
python -m mypy src/ --ignore-missing-imports --exclude="src/llm/router.py"
```

**Note on mypy:** The exclusion for `src/llm/router.py` is necessary to avoid conflicts with `src/fallback/router.py`.

## Project Architecture

The core logic is in the `src/` directory, which is organized into the following modules:

- `src/agents/`: Agent classes (planner, executor, base agent)
- `src/memory/`: Short-term and long-term memory modules
- `src/pipelines/`: Chat flows, document processing, task routing
- `src/retrieval/`: Vector search and document lookup
- `src/skills/`: Web search, code execution capabilities
- `src/vision_audio/`: Multimodal processing (image/audio)
- `src/prompt_engineering/`: Template management, few-shot, chaining
- `src/llm/`: OpenAI, Anthropic, custom LLM routing
- `src/fallback/`: Recovery logic when LLMs fail
- `src/guardrails/`: PII filters, output validation, safety
- `src/handlers/`: Input/output processing, error management
- `src/utils/`: Logging, caching, rate limiting, tokens

Other important directories:
- `config/`: YAML configurations for models, prompts, logging
- `data/`: Prompts, embeddings, dynamic content
- `examples/`: Minimal scripts demonstrating key features
- `test/`: Unit, integration, smoke, and e2e tests

## Key Development Rules

### ALWAYS:

1.  **Install dependencies** before making changes.
2.  **Set the `PYTHONPATH`** for all commands.
3.  **Run tests** (`PYTHONPATH=. python -m pytest test/ -v`) to validate the current state before making changes.
4.  **Configure the agent** by editing `config/model_config.yaml` before running it.
5.  **Ensure new Python modules** have proper `__init__.py` files.
6.  **Follow the branch naming convention**: `dev/<alias>/<feature>`.
7.  **Fill out the PR template** when submitting a pull request. The template is located at `.github/PULL_REQUEST_TEMPLATE.md`.

### NEVER:

-   Run tests without setting `PYTHONPATH`.
-   Assume `requirements.txt` contains dependencies.
-   Create modules named "router" (conflicts with existing router.py files).
-   Modify Azure pipeline scripts (`build/azure-pipelines/`) without TypeScript knowledge.
