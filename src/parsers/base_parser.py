"""
Base parser interface for diagram parsing.

This module defines the common interface and data structures for all diagram parsers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class DiagramType(Enum):
    """Supported diagram types."""
    PLANTUML = "plantuml"
    MERMAID = "mermaid"
    DRAWIO = "drawio"


class ElementType(Enum):
    """Types of diagram elements."""
    CLASS = "class"
    INTERFACE = "interface"
    COMPONENT = "component"
    ACTOR = "actor"
    USE_CASE = "use_case"
    RELATIONSHIP = "relationship"
    PACKAGE = "package"
    NOTE = "note"
    BOUNDARY = "boundary"
    CONTROL = "control"
    ENTITY = "entity"


@dataclass
class DiagramElement:
    """Represents a single element in a diagram."""
    id: str
    element_type: ElementType
    name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Dict[str, float]] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class DiagramRelationship:
    """Represents a relationship between diagram elements."""
    id: str
    source_id: str
    target_id: str
    relationship_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class ParsedDiagram:
    """Container for parsed diagram data."""
    diagram_type: DiagramType
    source_file: str
    elements: List[DiagramElement] = field(default_factory=list)
    relationships: List[DiagramRelationship] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class BaseParser(ABC):
    """Abstract base class for all diagram parsers."""
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """Return list of supported file extensions."""
        pass
    
    @property
    @abstractmethod
    def diagram_type(self) -> DiagramType:
        """Return the diagram type this parser handles."""
        pass
    
    @abstractmethod
    def parse(self, content: str, source_file: str = "") -> ParsedDiagram:
        """
        Parse diagram content and return structured data.
        
        Args:
            content: Raw diagram content (string)
            source_file: Optional source file path for context
            
        Returns:
            ParsedDiagram object containing extracted information
            
        Raises:
            ParseError: If content cannot be parsed
        """
        pass
    
    def parse_file(self, file_path: str) -> ParsedDiagram:
        """
        Parse diagram from file.
        
        Args:
            file_path: Path to diagram file
            
        Returns:
            ParsedDiagram object containing extracted information
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse(content, file_path)
    
    def validate_extension(self, file_path: str) -> bool:
        """Check if file extension is supported by this parser."""
        return any(file_path.lower().endswith(ext) for ext in self.supported_extensions)


class ParseError(Exception):
    """Exception raised when diagram parsing fails."""
    pass