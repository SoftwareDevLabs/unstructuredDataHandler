"""LangChain agent integration using OpenAI LLM and standard tools."""

import os
import yaml
from typing import Any, Optional, List

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

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
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        tools: Optional[List[Any]] = None,
        dry_run: bool = False,
        config_path: str = "config/model_config.yaml",
        **kwargs,
    ) -> None:
        """
        provider: 'gemini', 'openai', 'ollama', etc.
        api_key: API key for the provider (if required)
        model: Model name (if required)
        tools: Optional list of tools
        dry_run: If True, use a mock agent for testing.
        config_path: Path to the model configuration file.
        kwargs: Additional LLM-specific arguments
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        provider = provider or config.get('default_provider')
        provider = provider.lower()

        self.dry_run = bool(dry_run)
        self.llm: Any = None
        self.agent: Any = None
        self.store = {} # In-memory session store

        if self.dry_run:
            self.tools = tools or [EchoTool()]
            self.agent = MockAgent()
            return

        # Configure agent from YAML
        agent_config = config.get('agent', {})
        verbose = agent_config.get('verbose', True)

        # Configure provider
        provider_config = config.get('providers', {}).get(provider, {})
        model = model or provider_config.get('default_model')

        try:
            if provider == "gemini" or provider == "google":
                self.llm = GoogleGenerativeAI(google_api_key=api_key, model=model, **kwargs)
            elif provider == "openai":
                self.llm = OpenAI(openai_api_key=api_key, model=model, **kwargs)
            elif provider == "ollama" and Ollama is not None:
                self.llm = Ollama(model=model, **kwargs)
            else:
                raise ValueError(f"Unsupported or unavailable provider: {provider}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM provider '{provider}': {e}") from e

        self.tools = tools or [EchoTool()]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant."),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=self.tools, verbose=verbose)

        def get_session_history(session_id: str) -> ChatMessageHistory:
            if session_id not in self.store:
                self.store[session_id] = ChatMessageHistory()
            return self.store[session_id]

        self.agent = RunnableWithMessageHistory(
            agent_executor,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )


    def run(self, input_data: str, session_id: str = "default"):
        """
        Run the agent on the provided input data (prompt).
        """
        return self.agent.invoke(
            {"input": input_data},
            config={"configurable": {"session_id": session_id}},
        )


class MockAgent:
    """A trivial agent used for dry-run and CI that only echoes input."""
    def __init__(self):
        self.last_input = None

    def invoke(self, input_dict: dict, config: dict):
    def invoke(self, input: dict, config: dict):
        self.last_input = input["input"]
        return {"output": f"dry-run-echo:{self.last_input}"}


def main():
    """Main function to run the agent from the command line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Run agent in dry-run mode")
    parser.add_argument("--provider", help="LLM provider to use")
    parser.add_argument("--model", help="Model name to use")
    parser.add_argument("--prompt", default="What is the capital of France?", help="The prompt to run")
    parser.add_argument("--session-id", default="default", help="The session ID for the conversation")
    args = parser.parse_args()

    # Load environment variables from .env file
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

    api_key = None
    if not args.dry_run:
        if args.provider and (args.provider.lower() == "gemini" or args.provider.lower() == "google"):
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
        elif args.provider and args.provider.lower() == "openai":
            api_key = os.getenv("OPENAI_API_KEY")

    try:
        agent = SDLCFlexibleAgent(
            provider=args.provider,
            api_key=api_key,
            model=args.model,
            dry_run=args.dry_run,
        )
        result = agent.run(args.prompt, session_id=args.session_id)
        print("Agent result:", result)
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    main()
