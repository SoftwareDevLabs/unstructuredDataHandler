import pytest
from src.agents import deepagent

def test_sdlcflexibleagent_dry_run():
    """
    Tests that the SDLCFlexibleAgent in dry-run mode uses the MockAgent and returns the expected echo response.
    """
    # Arrange
    agent = deepagent.SDLCFlexibleAgent(dry_run=True)

    # Act
    resp = agent.run("hello")

    # Assert
    assert isinstance(agent.agent, deepagent.MockAgent)
    assert resp == {"output": "dry-run-echo:hello"}
