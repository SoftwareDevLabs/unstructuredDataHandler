import unittest
import os
from src.skills.parser_tool import ParserTool

class TestAgentParserIntegration(unittest.TestCase):
    """
    Test the ParserTool to ensure it integrates correctly with the parsers.
    A full agent integration test is complex due to the need for extensive mocking.
    This test verifies the tool's core functionality.
    """

    def setUp(self):
        """Set up a dummy diagram file for testing."""
        self.test_file = "test_diagram.puml"
        with open(self.test_file, "w") as f:
            f.write("@startuml\nclass Test\n@enduml")

    def tearDown(self):
        """Remove the dummy diagram file."""
        os.remove(self.test_file)

    def test_parser_tool_with_puml(self):
        """Test that the ParserTool can correctly parse a PlantUML file."""
        tool = ParserTool()
        result = tool._run(self.test_file)
        self.assertIn("Successfully parsed", result)
        self.assertIn("1 elements", result)

if __name__ == '__main__':
    unittest.main()
