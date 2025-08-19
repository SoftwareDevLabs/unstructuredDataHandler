# DeepAgent usage

This document describes `src/agents/deepagent.py` usage, required environment variables, and the safe dry-run mode.

Required environment variables (depending on provider):

- For Gemini/Google:
  - `LLM_PROVIDER=gemini` or `LLM_PROVIDER=google`
  - `GOOGLE_GEMINI_API_KEY` (must be provided via GitHub Secrets or local environment)
  - Optional: `LLM_MODEL` (defaults to `chat-bison-001`)

- For OpenAI:
  - `LLM_PROVIDER=openai`
  - `OPENAI_API_KEY` (must be provided via GitHub Secrets or local environment)
  - Optional: `LLM_MODEL` (defaults to `gpt-3.5-turbo`)

 - For Ollama (local server):
   - `LLM_PROVIDER=ollama`
   - Ensure a local Ollama server is running (default: `http://localhost:11434`)

Dry-run / CI-safe mode

The module supports a `DRY_RUN=true` environment variable that prevents network calls and forces the agent to use the built-in `EchoTool` only. This makes unit tests and CI runs deterministic and offline-friendly.

Example (dry run):

```bash
DRY_RUN=true LLM_PROVIDER=gemini python -c "import runpy; runpy.run_module('src.agents.deepagent', run_name='__main__')"
```

Tests

Unit tests mock `initialize_agent` to avoid any external requests. Run tests with:

```bash
PYTHONPATH=. python -m pytest -q
```

## Migration and CI notes

- Ollama can be used as a local LLM provider (good for on-prem or offline runs). However, for primary CI testing we prefer cloud providers (Gemini and OpenAI) because they are easier to run in CI and have stable HTTP APIs.
- If you want to run the provider matrix in CI (which exercises real provider adapters), use the workflow dispatch input `run_providers=true` when triggering the `Python Tests (consolidated)` workflow.
- For provider matrix runs you must provide credentials/secrets in the repository (for example `GOOGLE_GEMINI_API_KEY` and `OPENAI_API_KEY`). For private repos or to upload coverage, set `CODECOV_TOKEN` in the repository secrets.
- Note: API keys were intentionally removed from the repository `.env` file. Provide keys via one of the following:

  - GitHub Secrets (recommended for CI): add `GOOGLE_GEMINI_API_KEY` and/or `OPENAI_API_KEY` in repository Settings → Secrets → Actions.

  - Local environment (developer): export them in your shell:

    ```bash
    export GOOGLE_GEMINI_API_KEY="your-gemini-key"
    export OPENAI_API_KEY="your-openai-key"
    ```

  - Local dotenv (development only): create an untracked `.env.local` and set keys there; do NOT commit it.
- Run the providers matrix manually from the Actions tab: select `Python Tests (consolidated)` → `Run workflow` → set `run_providers` to `true`.
