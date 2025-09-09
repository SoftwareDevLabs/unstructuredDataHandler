# DeepAgent Usage

This document describes the usage of `src/agents/deepagent.py`, its configuration, and how to run and test it.

## Configuration

The `SDLCFlexibleAgent` is configured via the `config/model_config.yaml` file. This file allows you to set the default LLM provider, model, and agent settings.

Here is an example of the configuration file:
```yaml
default_provider: gemini
default_model: chat-bison-001

providers:
  gemini:
    default_model: chat-bison-001
  openai:
    default_model: gpt-3.5-turbo
  ollama:
    default_model: llama2

agent:
  type: ZERO_SHOT_REACT_DESCRIPTION
  verbose: true
  memory:
    enabled: true
    type: ConversationBufferMemory
```

You can override the default provider and model at runtime by passing the `--provider` and `--model` command-line arguments when running the agent.

## Memory and Sessions

The agent supports conversational memory. Each conversation is tracked by a session ID. You can provide a session ID when running the agent to maintain context across multiple turns.

## Running the Agent

You can run the agent from the command line using the `deepagent.py` script.

**Command-line arguments:**
- `--dry-run`: Run the agent in dry-run mode (no network calls).
- `--provider`: The LLM provider to use (e.g., `gemini`, `openai`, `ollama`).
- `--model`: The model name to use.
- `--prompt`: The prompt to run.
- `--session-id`: The session ID for the conversation.

**Example:**
```bash
python src/agents/deepagent.py --prompt "Hello, how are you?" --session-id "my-session"
```

## Testing the DeepAgent

### Unit Tests

Unit tests for the `deepagent` are located in `test/unit/test_deepagent.py` and `test/unit/test_deepagent_providers.py`. These tests use `pytest` and `monkeypatch` to test the agent's functionality in isolation, without making any network calls.

To run the unit tests, use the following command:
```bash
PYTHONPATH=. pytest test/unit/
```

### Integration Tests

Integration tests for the LLM providers are located in `test/integration/llm/test_llm_api.py`. These tests are designed to be run against real LLM providers and require valid API keys.

To run the integration tests, you will need to set up your API keys as described in the next section.

## API Keys

To use providers like Gemini and OpenAI, you need to provide API keys. There are several ways to do this:

-   **GitHub Secrets (recommended for CI):** Add `GOOGLE_GEMINI_API_KEY` and/or `OPENAI_API_KEY` in your repository's `Settings` → `Secrets` → `Actions`.
-   **Local environment variables:** Export the keys in your shell:
    ```bash
    export GOOGLE_GEMINI_API_KEY="your-gemini-key"
    export OPENAI_API_KEY="your-openai-key"
    ```
-   **`.env` file:** Create a `.env` file in the root of the repository and add your API keys there. You can copy the `.env.template` file to get started.
-   **`.env.local` file (development only):** For local development, you can create an untracked `.env.local` file and set your keys there. Do NOT commit this file to version control.

## Ollama Provider

The `deepagent` supports the Ollama provider for running LLMs locally. To use it, you need to have an Ollama server running on your local machine (default: `http://localhost:11434`).

You can run the agent with the Ollama provider like this:
```bash
python src/agents/deepagent.py --provider ollama --model llama2 --prompt "Why is the sky blue?"
```

## Migration and CI Notes

-   Ollama can be used as a local LLM provider, which is great for on-premise or offline development. However, for CI testing, we prefer cloud providers like Gemini and OpenAI because they are easier to run in a CI environment and have stable HTTP APIs.
-   If you want to run the provider matrix in CI, which exercises the real provider adapters, you can manually trigger the `Python Tests (consolidated)` workflow from the GitHub Actions tab and set the `run_providers` input to `true`.
-   For provider matrix runs, you must provide API keys as GitHub Secrets. For private repos or to upload code coverage, you can also set the `CODECOV_TOKEN` secret.
-   Run the providers matrix manually from the Actions tab: select `Python Tests (consolidated)` → `Run workflow` → set `run_providers` to `true`.
