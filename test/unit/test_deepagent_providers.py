import pytest
from src.agents import deepagent

class FakeLLM:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

def test_provider_selection_gemini(monkeypatch):
    monkeypatch.setattr(deepagent, 'GoogleGenerativeAI', lambda **kw: FakeLLM(**kw))
    monkeypatch.setattr(deepagent, 'create_tool_calling_agent', lambda llm, tools, prompt: None)
    monkeypatch.setattr(deepagent, 'AgentExecutor', lambda agent, tools, verbose: None)
    monkeypatch.setattr(deepagent, 'RunnableWithMessageHistory', lambda executor, get_session_history, input_messages_key, history_messages_key: None)
    agent = deepagent.SDLCFlexibleAgent(provider='gemini', api_key='x')
    assert isinstance(agent.llm, FakeLLM)

def test_provider_selection_openai(monkeypatch):
    monkeypatch.setattr(deepagent, 'OpenAI', lambda **kw: FakeLLM(**kw))
    monkeypatch.setattr(deepagent, 'create_tool_calling_agent', lambda llm, tools, prompt: None)
    monkeypatch.setattr(deepagent, 'AgentExecutor', lambda agent, tools, verbose: None)
    monkeypatch.setattr(deepagent, 'RunnableWithMessageHistory', lambda executor, get_session_history, input_messages_key, history_messages_key: None)
    agent = deepagent.SDLCFlexibleAgent(provider='openai', api_key='openai-key')
    assert isinstance(agent.llm, FakeLLM)

def test_provider_selection_ollama(monkeypatch):
    if deepagent.Ollama is not None:
        monkeypatch.setattr(deepagent, 'Ollama', lambda **kw: FakeLLM(**kw))
        monkeypatch.setattr(deepagent, 'create_tool_calling_agent', lambda llm, tools, prompt: None)
        monkeypatch.setattr(deepagent, 'AgentExecutor', lambda agent, tools, verbose: None)
        monkeypatch.setattr(deepagent, 'RunnableWithMessageHistory', lambda executor, get_session_history, input_messages_key, history_messages_key: None)
        agent = deepagent.SDLCFlexibleAgent(provider='ollama')
        assert isinstance(agent.llm, FakeLLM)
    else:
        with pytest.raises(ValueError):
            deepagent.SDLCFlexibleAgent(provider='ollama')

def test_dry_run_flag():
    agent = deepagent.SDLCFlexibleAgent(dry_run=True)
    assert agent.llm is None
    assert isinstance(agent.agent, deepagent.MockAgent)
    assert agent.run("test") == {"output": "dry-run-echo:test"}
