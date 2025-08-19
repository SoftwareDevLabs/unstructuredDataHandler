import pytest
from types import SimpleNamespace

# Import the module under test
from src.agents import deepagent


class DummyLLM:
    """A minimal LLM-like object that provides a generate or call-like interface used by LangChain."""
    def __init__(self, response_text="Dummy response"):
        self.response_text = response_text

    def __call__(self, *args, **kwargs):
        return self.response_text

    async def agenerate(self, *args, **kwargs):
        class R:
            generations = [[SimpleNamespace(text=self.response_text)]]
        return R()


class DummyAgent:
    def __init__(self):
        self.last_input = None

    def run(self, input_data: str):
        self.last_input = input_data
        return f"mock-run:{input_data}"


def test_sdlcflexibleagent_with_mocked_llm(monkeypatch):
    # Arrange: replace initialize_agent with a factory that returns our DummyAgent
    monkeypatch.setattr(deepagent, "initialize_agent", lambda tools, llm, agent, verbose: DummyAgent())

    # Also bypass provider selection by directly constructing the agent and injecting a dummy LLM
    agent = deepagent.SDLCFlexibleAgent.__new__(deepagent.SDLCFlexibleAgent)
    agent.llm = DummyLLM()
    agent.tools = [deepagent.EchoTool()]
    agent.agent = deepagent.initialize_agent(agent.tools, agent.llm, agent=None, verbose=False)

    # Act
    resp = deepagent.SDLCFlexibleAgent.run(agent, "hello")

    # Assert
    assert resp == "mock-run:hello"
    assert agent.agent.last_input == "hello"
