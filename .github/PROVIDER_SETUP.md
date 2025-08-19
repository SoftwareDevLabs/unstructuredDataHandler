
# GitHub CI: Provider secrets & manual provider matrix

This file documents the repository secrets and quick steps to run provider-specific CI jobs manually.

- Add `GOOGLE_GEMINI_API_KEY` to your environment before running provider jobs.

- GitHub Actions / Secrets

To store provider keys for CI, add them as repository secrets. Example using the GitHub CLI:

```bash
# store a Gemini key
gh secret set GOOGLE_GEMINI_API_KEY --body "<your-gemini-key>"

# store an OpenAI key
gh secret set OPENAI_API_KEY --body "<your-openai-key>"

# optionally, store Codecov token
gh secret set CODECOV_TOKEN --body "<your-codecov-token>"
```

- Local dev note: Do not commit API keys into the repository. The project `.env` file has been sanitized and no longer contains live API keys. For local development, either export the variables in your shell or create a `.env.local` file which is gitignored.

- `OPENAI_API_KEY` — API key for OpenAI (if you run OpenAI provider jobs).

- `CODECOV_TOKEN` — (optional) Codecov token for private repos if you want coverage uploaded. Public repos usually don't need this.

Notes about Ollama:

- Ollama is a local inference server. The CI provider matrix includes `ollama` as an option but most CI runs should use `gemini` or `openai` unless you have an Ollama server available in your runner.

- If you want to run Ollama in CI, you must either run a self-hosted runner that has Ollama installed and running, or start an Ollama container as part of the job before running tests.


Or set them manually in the GitHub UI:
- Repo → Settings → Secrets and variables → Actions → New repository secret


How to run the provider matrix manually

1. Open the repository on GitHub and go to Actions → `Python Tests (consolidated)`.
2. Click "Run workflow" and set `run_providers` to `true` then dispatch.

Or use the `gh` CLI to dispatch the workflow (example):

```bash
# Replace 'python-test.yml' with the workflow file name if different
gh workflow run python-test.yml -f run_providers=true
```

If you prefer to run a single provider smoke job manually (quick check) use the provider-smoke job in the workflow (via the Actions UI) or run a small script locally that constructs the agent with `dry_run=True`:

```bash
# Dry-run locally (no network calls) — uses gemini by default in examples
DRY_RUN=true LLM_PROVIDER=gemini python -c "from src.agents import deepagent; a=deepagent.SDLCFlexibleAgent(provider='gemini', dry_run=True); print('dry run ok', a.agent.run('hello'))"
```

Security

- Never commit secrets to the repository.
- Use least-privilege credentials for CI runs when possible.

Troubleshooting

- If the `providers` matrix job fails for `ollama`, check that the runner has network access to your Ollama server or that a local Ollama container was started prior to running tests.
- For Codecov failures, ensure `CODECOV_TOKEN` is set if the repo is private.

Running Ollama in CI (example)

If you want to spin up an Ollama container in a job before running tests, you can add a step like this (example using Docker):

```yaml
- name: Start Ollama container
	run: |
		docker run -d --name ollama -p 11434:11434 ollama/ollama:latest
		# optionally wait for health endpoint
		until curl -sSf http://localhost:11434/health; do sleep 1; done
```

Note: replace `ollama/ollama:latest` with the image/tag you prefer. For GitHub-hosted runners, ensure Docker is available or use a self-hosted runner with Ollama installed.
