"""
Parser module for processing different diagram formats (UML/SYSML).

This module provides parsers for:
- PlantUML (.puml, .plantuml)
- Mermaid (.mmd, .mermaid) 
- DrawIO (.drawio, .xml)

The parsers extract information from diagram sources and create structured data
with relevant tags for downstream tool implementations.
"""

from .base_parser import BaseParser, ParsedDiagram
from .plantuml_parser import PlantUMLParser
from .mermaid_parser import MermaidParser
from .drawio_parser import DrawIOParser

__all__ = [
    'BaseParser',
    'ParsedDiagram',
    'PlantUMLParser', 
    'MermaidParser',
    'DrawIOParser'
]