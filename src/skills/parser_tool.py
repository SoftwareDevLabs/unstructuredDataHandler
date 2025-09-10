from langchain.tools import BaseTool
from typing import Type
from src.parsers import DrawIOParser, MermaidParser, PlantUMLParser
from pydantic import BaseModel, Field

class FilePathInput(BaseModel):
    file_path: str = Field(description="The path to the diagram file to parse.")

class ParserTool(BaseTool):
    name: str = "DiagramParserTool"
    description: str = "Parses a diagram file (DrawIO, Mermaid, or PlantUML) and returns a summary of its contents."
    args_schema: Type[BaseModel] = FilePathInput

    def _run(self, file_path: str) -> str:
        """Use the tool."""
        try:
            # This is a simplified parser selection logic.
            # A more robust implementation would use a factory or registration pattern.
            if file_path.endswith(('.drawio', '.xml')):
                parser = DrawIOParser()
            elif file_path.endswith(('.mmd', '.mermaid')):
                parser = MermaidParser()
            elif file_path.endswith(('.puml', '.plantuml', '.pu')):
                parser = PlantUMLParser()
            else:
                return f"Error: Unsupported file type for {file_path}"

            diagram = parser.parse_file(file_path)
            summary = f"Successfully parsed {file_path}. "
            summary += f"Found {len(diagram.elements)} elements and {len(diagram.relationships)} relationships."
            return summary
        except Exception as e:
            return f"Error parsing file {file_path}: {e}"

    async def _arun(self, file_path: str) -> str:
        """Use the tool asynchronously."""
        return self._run(file_path)
