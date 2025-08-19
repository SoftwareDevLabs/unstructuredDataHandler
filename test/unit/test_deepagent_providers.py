from types import SimpleNamespace
import pytest

from src.agents import deepagent


class FakeLLM:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_provider_selection_gemini(monkeypatch):
    # Patch GoogleGenerativeAI to our fake
    monkeypatch.setattr(deepagent, 'GoogleGenerativeAI', lambda **kw: FakeLLM(**kw))
    # Prevent LangChain from validating the LLM by returning a MockAgent
    monkeypatch.setattr(deepagent, 'initialize_agent', lambda tools, llm, agent, verbose: deepagent.MockAgent())
    agent = deepagent.SDLCFlexibleAgent(provider='gemini', api_key='x', model='chat-bison-001', tools=[deepagent.EchoTool()])
    assert isinstance(agent.llm, FakeLLM)


def test_provider_selection_openai(monkeypatch):
    monkeypatch.setattr(deepagent, 'OpenAI', lambda **kw: FakeLLM(**kw))
    monkeypatch.setattr(deepagent, 'initialize_agent', lambda tools, llm, agent, verbose: deepagent.MockAgent())
    agent = deepagent.SDLCFlexibleAgent(provider='openai', api_key='openai-key', model='gpt-3.5', tools=[deepagent.EchoTool()])
    assert isinstance(agent.llm, FakeLLM)


def test_provider_selection_ollama(monkeypatch):
    # If Ollama is present, patch it; else ensure constructor raises for missing provider
    if deepagent.Ollama is not None:
        monkeypatch.setattr(deepagent, 'Ollama', lambda **kw: FakeLLM(**kw))
        monkeypatch.setattr(deepagent, 'initialize_agent', lambda tools, llm, agent, verbose: deepagent.MockAgent())
        agent = deepagent.SDLCFlexibleAgent(provider='ollama', model='llama2', tools=[deepagent.EchoTool()])
        assert isinstance(agent.llm, FakeLLM)
    else:
        with pytest.raises(ValueError):
            deepagent.SDLCFlexibleAgent(provider='ollama')


def test_dry_run_flag():
    agent = deepagent.SDLCFlexibleAgent(provider='gemini', dry_run=True)
    # In dry-run mode llm should be None and agent is a MockAgent
    assert agent.llm is None
    assert hasattr(agent, 'agent')
    assert agent.agent.run('x') == 'dry-run-echo:x'
