"""
Tests for the base parser interface.
"""

import pytest
from src.parsers.base_parser import (
    BaseParser, ParsedDiagram, DiagramElement, DiagramRelationship,
    DiagramType, ElementType, ParseError
)


class TestDiagramElement:
    """Test DiagramElement dataclass."""
    
    def test_element_creation(self):
        """Test creating a diagram element."""
        element = DiagramElement(
            id="test_id",
            element_type=ElementType.CLASS,
            name="TestClass",
            properties={"visibility": "public"},
            position={"x": 10.0, "y": 20.0},
            tags=["important"]
        )
        
        assert element.id == "test_id"
        assert element.element_type == ElementType.CLASS
        assert element.name == "TestClass"
        assert element.properties["visibility"] == "public"
        assert element.position["x"] == 10.0
        assert element.tags == ["important"]
    
    def test_element_default_values(self):
        """Test element creation with default values."""
        element = DiagramElement(
            id="simple",
            element_type=ElementType.COMPONENT,
            name="Simple"
        )
        
        assert element.properties == {}
        assert element.position is None
        assert element.tags == []


class TestDiagramRelationship:
    """Test DiagramRelationship dataclass."""
    
    def test_relationship_creation(self):
        """Test creating a diagram relationship."""
        relationship = DiagramRelationship(
            id="rel_1",
            source_id="A",
            target_id="B",
            relationship_type="inheritance",
            properties={"multiplicity": "1..*"},
            tags=["important"]
        )
        
        assert relationship.id == "rel_1"
        assert relationship.source_id == "A"
        assert relationship.target_id == "B"
        assert relationship.relationship_type == "inheritance"
        assert relationship.properties["multiplicity"] == "1..*"
        assert relationship.tags == ["important"]


class TestParsedDiagram:
    """Test ParsedDiagram dataclass."""
    
    def test_diagram_creation(self):
        """Test creating a parsed diagram."""
        element = DiagramElement(
            id="elem1",
            element_type=ElementType.CLASS,
            name="TestClass"
        )
        
        relationship = DiagramRelationship(
            id="rel1",
            source_id="elem1",
            target_id="elem2",
            relationship_type="association"
        )
        
        diagram = ParsedDiagram(
            diagram_type=DiagramType.PLANTUML,
            source_file="test.puml",
            elements=[element],
            relationships=[relationship],
            metadata={"title": "Test Diagram"},
            tags=["test"]
        )
        
        assert diagram.diagram_type == DiagramType.PLANTUML
        assert diagram.source_file == "test.puml"
        assert len(diagram.elements) == 1
        assert len(diagram.relationships) == 1
        assert diagram.metadata["title"] == "Test Diagram"
        assert diagram.tags == ["test"]


class MockParser(BaseParser):
    """Mock parser for testing base functionality."""
    
    @property
    def supported_extensions(self):
        return ['.mock']
    
    @property
    def diagram_type(self):
        return DiagramType.PLANTUML
    
    def parse(self, content, source_file=""):
        return ParsedDiagram(
            diagram_type=self.diagram_type,
            source_file=source_file
        )


class TestBaseParser:
    """Test BaseParser abstract base class."""
    
    def test_validate_extension(self):
        """Test file extension validation."""
        parser = MockParser()
        
        assert parser.validate_extension("test.mock") is True
        assert parser.validate_extension("test.MOCK") is True
        assert parser.validate_extension("test.txt") is False
    
    def test_parse_file(self, tmp_path):
        """Test parsing from file."""
        parser = MockParser()
        
        # Create test file
        test_file = tmp_path / "test.mock"
        test_file.write_text("test content")
        
        result = parser.parse_file(str(test_file))
        
        assert result.diagram_type == DiagramType.PLANTUML
        assert result.source_file == str(test_file)
    
    def test_abstract_methods(self):
        """Test that BaseParser is properly abstract."""
        with pytest.raises(TypeError):
            BaseParser()


class TestEnums:
    """Test enum definitions."""
    
    def test_diagram_type_enum(self):
        """Test DiagramType enum values."""
        assert DiagramType.PLANTUML.value == "plantuml"
        assert DiagramType.MERMAID.value == "mermaid"
        assert DiagramType.DRAWIO.value == "drawio"
    
    def test_element_type_enum(self):
        """Test ElementType enum values."""
        assert ElementType.CLASS.value == "class"
        assert ElementType.INTERFACE.value == "interface"
        assert ElementType.COMPONENT.value == "component"
        assert ElementType.ACTOR.value == "actor"


class TestParseError:
    """Test ParseError exception."""
    
    def test_parse_error_creation(self):
        """Test creating ParseError."""
        error = ParseError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)