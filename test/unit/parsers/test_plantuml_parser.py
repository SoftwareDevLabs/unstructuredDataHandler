"""
Tests for PlantUML parser.
"""

import pytest
from src.parsers.plantuml_parser import PlantUMLParser
from src.parsers.base_parser import DiagramType, ElementType, ParseError


class TestPlantUMLParser:
    """Test PlantUML parser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = PlantUMLParser()
    
    def test_supported_extensions(self):
        """Test supported file extensions."""
        extensions = self.parser.supported_extensions
        assert '.puml' in extensions
        assert '.plantuml' in extensions
        assert '.pu' in extensions
    
    def test_diagram_type(self):
        """Test diagram type property."""
        assert self.parser.diagram_type == DiagramType.PLANTUML
    
    def test_parse_simple_class(self):
        """Test parsing a simple class definition."""
        content = """
        @startuml
        class TestClass {
            +attribute1 : String
            -attribute2 : int
            +method1() : void
        }
        @enduml
        """
        
        result = self.parser.parse(content, "test.puml")
        
        assert result.diagram_type == DiagramType.PLANTUML
        assert result.source_file == "test.puml"
        assert len(result.elements) == 1
        
        element = result.elements[0]
        assert element.id == "TestClass"
        assert element.element_type == ElementType.CLASS
        assert element.name == "TestClass"
        assert "attributes" in element.properties
        assert "methods" in element.properties
    
    def test_parse_interface(self):
        """Test parsing interface definition."""
        content = """
        @startuml
        interface ITestInterface {
            +method1() : void
            +method2(param : String) : int
        }
        @enduml
        """
        
        result = self.parser.parse(content)
        
        assert len(result.elements) == 1
        element = result.elements[0]
        assert element.element_type == ElementType.INTERFACE
        assert element.name == "ITestInterface"
    
    def test_parse_actor(self):
        """Test parsing actor definition."""
        content = """
        @startuml
        actor User
        actor Administrator as Admin
        @enduml
        """
        
        result = self.parser.parse(content)
        
        assert len(result.elements) == 2
        
        user_element = next(e for e in result.elements if e.name == "User")
        assert user_element.element_type == ElementType.ACTOR
        assert user_element.id == "User"
        
        admin_element = next(e for e in result.elements if e.name == "Administrator")
        assert admin_element.element_type == ElementType.ACTOR
        assert admin_element.id == "Admin"
    
    def test_parse_inheritance_relationship(self):
        """Test parsing inheritance relationships."""
        content = """
        @startuml
        class Parent
        class Child
        Parent <|-- Child
        @enduml
        """
        
        result = self.parser.parse(content)
        
        assert len(result.elements) == 2
        assert len(result.relationships) == 1
        
        relationship = result.relationships[0]
        assert relationship.relationship_type == "inheritance"
        assert relationship.source_id == "Parent"
        assert relationship.target_id == "Child"
    
    def test_parse_composition_relationship(self):
        """Test parsing composition relationships."""
        content = """
        @startuml
        class Car
        class Engine
        Car *-- Engine
        @enduml
        """
        
        result = self.parser.parse(content)
        
        assert len(result.relationships) == 1
        relationship = result.relationships[0]
        assert relationship.relationship_type == "composition"
        assert relationship.source_id == "Car"
        assert relationship.target_id == "Engine"
    
    def test_parse_association_relationship(self):
        """Test parsing association relationships."""
        content = """
        @startuml
        class Person
        class Company
        Person --> Company : works for
        @enduml
        """
        
        result = self.parser.parse(content)
        
        assert len(result.relationships) == 1
        relationship = result.relationships[0]
        assert relationship.relationship_type == "association"
        assert relationship.source_id == "Person"
        assert relationship.target_id == "Company"
    
    def test_parse_metadata(self):
        """Test parsing diagram metadata."""
        content = """
        @startuml
        title Test Diagram Title
        skinparam classBackgroundColor lightblue
        skinparam classBorderColor black
        
        class TestClass
        
        note right : This is a test note
        @enduml
        """
        
        result = self.parser.parse(content)
        
        assert "title" in result.metadata
        assert result.metadata["title"] == "Test Diagram Title"
        assert "skinparams" in result.metadata
        assert "notes" in result.metadata
    
    def test_clean_content(self):
        """Test content cleaning functionality."""
        content = """
        @startuml
        ' This is a comment
        class TestClass {
            +method() : void
        }
        /' This is a 
           multi-line comment '/
        class AnotherClass
        @enduml
        """
        
        cleaned = self.parser._clean_content(content)
        
        # Comments should be removed
        assert "This is a comment" not in cleaned
        assert "multi-line comment" not in cleaned
        # Important content should remain
        assert "TestClass" in cleaned
        assert "AnotherClass" in cleaned
    
    def test_parse_class_with_stereotype(self):
        """Test parsing class with stereotype."""
        content = """
        @startuml
        class TestClass <<Entity>> {
            +id : Long
        }
        @enduml
        """
        
        result = self.parser.parse(content)
        
        assert len(result.elements) == 1
        element = result.elements[0]
        assert element.properties.get("stereotype") == "Entity"
    
    def test_parse_component(self):
        """Test parsing component definition."""
        content = """
        @startuml
        component WebServer
        component Database as DB
        @enduml
        """
        
        result = self.parser.parse(content)
        
        assert len(result.elements) == 2
        
        web_server = next(e for e in result.elements if e.name == "WebServer")
        assert web_server.element_type == ElementType.COMPONENT
        
        database = next(e for e in result.elements if e.name == "Database")
        assert database.element_type == ElementType.COMPONENT
        assert database.id == "DB"
    
    def test_parse_empty_content(self):
        """Test parsing empty content."""
        result = self.parser.parse("")
        
        assert result.diagram_type == DiagramType.PLANTUML
        assert len(result.elements) == 0
        assert len(result.relationships) == 0
    
    def test_parse_invalid_content(self):
        """Test error handling for invalid content."""
        # This should not raise an exception, but should handle gracefully
        content = "invalid plantuml content"
        result = self.parser.parse(content)
        
        assert result.diagram_type == DiagramType.PLANTUML
        # Should still return a result, even if empty
        assert isinstance(result.elements, list)
        assert isinstance(result.relationships, list)
    
    def test_parse_multiple_relationships(self):
        """Test parsing multiple relationship types."""
        content = """
        @startuml
        class A
        class B
        class C
        class D
        
        A --|> B : inheritance
        A *-- C : composition
        A o-- D : aggregation
        A ..> B : dependency
        @enduml
        """
        
        result = self.parser.parse(content)
        
        assert len(result.relationships) == 4
        
        rel_types = [rel.relationship_type for rel in result.relationships]
        assert "inheritance" in rel_types
        assert "composition" in rel_types
        assert "aggregation" in rel_types
        assert "dependency" in rel_types