"""LangChain agent integration using OpenAI LLM and standard tools."""

from typing import Any, Optional, List

from langchain.agents import initialize_agent, AgentType

# LLM names declared as Any so mypy accepts fallback to None if imports fail
GoogleGenerativeAI: Any
OpenAI: Any
Ollama: Any

try:
    from langchain_google_genai.llms import GoogleGenerativeAI  # type: ignore
except Exception:
    GoogleGenerativeAI = None

try:
    from langchain_community.llms import OpenAI  # type: ignore
except Exception:
    OpenAI = None

try:
    from langchain_community.llms import Ollama  # type: ignore
except Exception:
    Ollama = None

# Simple custom echo tool for demonstration
from langchain.tools import BaseTool


class EchoTool(BaseTool):
    name: str = "EchoTool"
    description: str = "Echoes the input back to the user."

    def _run(self, query: str):
        return f"Echo: {query}"

    async def _arun(self, query: str):
        return f"Echo: {query}"


class SDLCFlexibleAgent:
    """
    SDLC Agent supporting multiple LLM providers (Gemini, OpenAI, Ollama, etc.).
    """
    def __init__(
        self,
        provider: str,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        dry_run: bool = False,
        **kwargs,
    ) -> None:
        """
        provider: 'gemini', 'openai', 'ollama', etc.
        api_key: API key for the provider (if required)
        model: Model name (if required)
        tools: Optional list of tools
        kwargs: Additional LLM-specific arguments
        """
        provider = provider.lower()
        self.dry_run = bool(dry_run)
        # typed instance attributes for mypy
        self.llm: Any = None
        self.agent: Any = None
        # In dry-run mode, avoid creating real LLMs or network calls
        if self.dry_run:
            # Use a no-network mock LLM and a MockAgent below
            self.llm = None
            if tools is None:
                self.tools = [EchoTool()]
            else:
                self.tools = tools
            self.agent = MockAgent()
            return
        if provider == "gemini" or provider == "google":
            # Use GoogleGenerativeAI from langchain-google-genai
            gemini_model = model or "chat-bison-001"
            self.llm = GoogleGenerativeAI(
                google_api_key=api_key,
                model=gemini_model,
                **kwargs,
            )
        elif provider == "openai":
            self.llm = OpenAI(openai_api_key=api_key, model=model or "gpt-3.5-turbo", **kwargs)
        elif provider == "ollama" and Ollama is not None:
            self.llm = Ollama(model=model or "llama2", **kwargs)
        else:
            raise ValueError(f"Unsupported or unavailable provider: {provider}")
        if tools is None:
            self.tools = [EchoTool()]
        else:
            self.tools = tools
        # initialize_agent returns an executor; keep as Any for flexibility in dry-run tests
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=not self.dry_run,
        )

    def run(self, input_data: str):
        """
        Run the agent on the provided input data (prompt).
        """
        # If dry-run, MockAgent implements run; otherwise call the agent
        return self.agent.run(input_data)


class MockAgent:
    """A trivial agent used for dry-run and CI that only echoes input."""
    def __init__(self):
        self.last_input = None

    def run(self, input_data: str):
        self.last_input = input_data
        return f"dry-run-echo:{input_data}"


if __name__ == "__main__":
    import os
    import argparse
    from dotenv import load_dotenv

    # Load environment variables from .env file in the repo root
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Run agent in dry-run (no network) mode")
    parser.add_argument("--provider", dest="provider", default=None, help="LLM provider to use (overrides LLM_PROVIDER env var)")
    parser.add_argument("--model", dest="model", default=None, help="Model name to use (overrides LLM_MODEL env var)")
    args = parser.parse_args()

    provider = args.provider or os.getenv("LLM_PROVIDER", "gemini")
    model = args.model or os.getenv("LLM_MODEL", None)
    api_key = None

    # DRY_RUN environment or flag
    dry_run_env = os.getenv("DRY_RUN", "false").lower() in ("1", "true", "yes")
    dry_run = dry_run_env or bool(args.dry_run)

    if not dry_run:
        if provider.lower() == "gemini" or provider.lower() == "google":
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY not found in environment or .env file.")
        elif provider.lower() == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment or .env file.")
        elif provider.lower() == "ollama":
            api_key = None  # Ollama may not require an API key
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    agent = SDLCFlexibleAgent(provider=provider, api_key=api_key, model=model, dry_run=dry_run)
    prompt = "What is the capital of France?"
    result = agent.run(prompt)
    print("Agent result:", result)
