import unittest
from unittest.mock import patch, mock_open
import pytest

from src.agents.deepagent import SDLCFlexibleAgent

class TestDeepAgentCoverage(unittest.TestCase):
    """
    Test suite to improve coverage for the DeepAgent module.
    """

    def test_unsupported_provider_raises_runtime_error(self):
        """
        Test that requesting an unsupported provider raises a RuntimeError.
        """
        with self.assertRaises(RuntimeError):
            SDLCFlexibleAgent(provider="unsupported_provider")

    @patch('src.agents.deepagent.SDLCFlexibleAgent.run')
    def test_main_function_dry_run(self, mock_run):
        """
        Test the main function with the --dry-run flag.
        """
        from src.agents.deepagent import main

        with patch('sys.argv', ['deepagent.py', '--dry-run', '--prompt', 'test prompt']):
            main()
            mock_run.assert_called_once_with('test prompt', session_id='default')

    def test_run_method_invokes_agent(self):
        """
        Test that the run method correctly invokes the agent's invoke method.
        """
        agent = SDLCFlexibleAgent(dry_run=True)

        with patch.object(agent.agent, 'invoke', return_value="mocked_output") as mock_invoke:
            result = agent.run("test input")
            mock_invoke.assert_called_once_with(
                {"input": "test input"},
                config={"configurable": {"session_id": "default"}},
            )
            self.assertEqual(result, "mocked_output")

if __name__ == '__main__':
    unittest.main()
