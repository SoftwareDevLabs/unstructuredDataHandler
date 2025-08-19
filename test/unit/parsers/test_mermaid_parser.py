"""
Tests for Mermaid parser.
"""

import pytest
from src.parsers.mermaid_parser import MermaidParser
from src.parsers.base_parser import DiagramType, ElementType, ParseError


class TestMermaidParser:
    """Test Mermaid parser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = MermaidParser()
    
    def test_supported_extensions(self):
        """Test supported file extensions."""
        extensions = self.parser.supported_extensions
        assert '.mmd' in extensions
        assert '.mermaid' in extensions
    
    def test_diagram_type(self):
        """Test diagram type property."""
        assert self.parser.diagram_type == DiagramType.MERMAID
    
    def test_detect_mermaid_type(self):
        """Test Mermaid diagram type detection."""
        class_content = "classDiagram\nclass TestClass"
        assert self.parser._detect_mermaid_type(class_content) == "classDiagram"
        
        sequence_content = "sequenceDiagram\nA->>B: Message"
        assert self.parser._detect_mermaid_type(sequence_content) == "sequenceDiagram"
        
        flowchart_content = "flowchart TD\nA --> B"
        assert self.parser._detect_mermaid_type(flowchart_content) == "flowchart"
        
        graph_content = "graph LR\nA --> B"
        assert self.parser._detect_mermaid_type(graph_content) == "graph"
    
    def test_parse_class_diagram(self):
        """Test parsing Mermaid class diagram."""
        content = """
        classDiagram
        class Animal {
            +String name
            +int age
            +makeSound() void
        }
        class Dog {
            +String breed
            +bark() void
        }
        Animal <|-- Dog
        """
        
        result = self.parser.parse(content, "test.mmd")
        
        assert result.diagram_type == DiagramType.MERMAID
        assert result.source_file == "test.mmd"
        assert result.metadata["mermaid_type"] == "classDiagram"
        
        # Should have parsed classes
        class_elements = [e for e in result.elements if e.element_type == ElementType.CLASS]
        assert len(class_elements) >= 1
        
        # Should have parsed inheritance relationship
        inheritance_rels = [r for r in result.relationships if r.relationship_type == "inheritance"]
        assert len(inheritance_rels) >= 1
    
    def test_parse_flowchart(self):
        """Test parsing Mermaid flowchart."""
        content = """
        flowchart TD
        A[Start] --> B{Decision}
        B -->|Yes| C[Process 1]
        B -->|No| D[Process 2]
        C --> E[End]
        D --> E
        """
        
        result = self.parser.parse(content)
        
        assert result.metadata["mermaid_type"] == "flowchart"
        
        # Should have parsed nodes
        assert len(result.elements) >= 4
        
        # Check for different node shapes
        rect_nodes = [e for e in result.elements if e.properties.get("shape") == "rectangular"]
        diamond_nodes = [e for e in result.elements if e.properties.get("shape") == "diamond"]
        
        assert len(rect_nodes) >= 1
        assert len(diamond_nodes) >= 1
        
        # Should have parsed connections
        assert len(result.relationships) >= 4
    
    def test_parse_sequence_diagram(self):
        """Test parsing Mermaid sequence diagram."""
        content = """
        sequenceDiagram
        participant A as Alice
        participant B as Bob
        A->>B: Hello Bob, how are you?
        B-->>A: Great!
        A->>B: See you later!
        """
        
        result = self.parser.parse(content)
        
        assert result.metadata["mermaid_type"] == "sequenceDiagram"
        
        # Should have parsed participants
        actors = [e for e in result.elements if e.element_type == ElementType.ACTOR]
        assert len(actors) == 2
        
        # Check participant names
        alice = next((a for a in actors if a.name == "Alice"), None)
        bob = next((a for a in actors if a.name == "Bob"), None)
        assert alice is not None
        assert bob is not None
        
        # Should have parsed messages
        assert len(result.relationships) >= 3
        
        # Check message types
        async_msgs = [r for r in result.relationships if r.relationship_type == "async_message"]
        return_msgs = [r for r in result.relationships if r.relationship_type == "return_message"]
        
        assert len(async_msgs) >= 2
        assert len(return_msgs) >= 1
    
    def test_parse_er_diagram(self):
        """Test parsing Mermaid ER diagram."""
        content = """
        erDiagram
        CUSTOMER {
            string name
            string email
            int age
        }
        ORDER {
            int order_id
            date order_date
            float total
        }
        CUSTOMER ||--o{ ORDER : places
        """
        
        result = self.parser.parse(content)
        
        assert result.metadata["mermaid_type"] == "erDiagram"
        
        # Should have parsed entities
        entities = [e for e in result.elements if e.element_type == ElementType.ENTITY]
        assert len(entities) == 2
        
        # Check entity attributes
        customer = next((e for e in entities if e.name == "CUSTOMER"), None)
        assert customer is not None
        assert len(customer.properties.get("attributes", [])) == 3
        
        # Should have parsed relationship
        assert len(result.relationships) == 1
        relationship = result.relationships[0]
        assert relationship.relationship_type == "one_to_many"
    
    def test_parse_graph_diagram(self):
        """Test parsing Mermaid graph diagram."""
        content = """
        graph LR
        A --> B
        A --> C
        B --> D
        C --> D
        """
        
        result = self.parser.parse(content)
        
        assert result.metadata["mermaid_type"] == "graph"
        
        # Should have parsed nodes and connections
        assert len(result.elements) >= 4
        assert len(result.relationships) >= 4
    
    def test_clean_content(self):
        """Test content cleaning functionality."""
        content = """
        classDiagram
        %% This is a comment
        class TestClass {
            +method() void
        }
        %% Another comment
        class AnotherClass
        """
        
        cleaned = self.parser._clean_content(content)
        
        assert "This is a comment" not in cleaned
        assert "Another comment" not in cleaned
        assert "TestClass" in cleaned
        assert "AnotherClass" in cleaned
    
    def test_parse_class_relationships(self):
        """Test parsing various class relationships."""
        content = """
        classDiagram
        class A
        class B
        class C
        class D
        
        A <|-- B
        A *-- C
        A o-- D
        A --> B
        A ..> C
        """
        
        result = self.parser.parse(content)
        
        assert len(result.relationships) >= 4
        
        rel_types = [rel.relationship_type for rel in result.relationships]
        assert "inheritance" in rel_types
        assert "composition" in rel_types
        assert "aggregation" in rel_types
        assert "association" in rel_types
    
    def test_parse_flowchart_node_shapes(self):
        """Test parsing different flowchart node shapes."""
        content = """
        flowchart TD
        A[Rectangle]
        B(Rounded)
        C{Diamond}
        D((Circle))
        """
        
        result = self.parser.parse(content)
        
        # Should recognize different shapes
        shapes = [e.properties.get("shape") for e in result.elements]
        assert "rectangular" in shapes
        assert "rounded" in shapes
        assert "diamond" in shapes
        assert "circle" in shapes
    
    def test_parse_empty_content(self):
        """Test parsing empty content."""
        result = self.parser.parse("")
        
        assert result.diagram_type == DiagramType.MERMAID
        assert len(result.elements) == 0
        assert len(result.relationships) == 0
    
    def test_parse_unknown_diagram_type(self):
        """Test parsing unknown diagram type."""
        content = """
        unknownDiagram
        A --> B
        """
        
        result = self.parser.parse(content)
        
        assert result.metadata["mermaid_type"] == "unknown"
        # Should still attempt to parse generically
        assert isinstance(result.elements, list)
        assert isinstance(result.relationships, list)
    
    def test_parse_sequence_with_auto_participants(self):
        """Test sequence diagram that auto-creates participants."""
        content = """
        sequenceDiagram
        Alice->>Bob: Hello
        Bob->>Charlie: Forward message
        """
        
        result = self.parser.parse(content)
        
        # Should auto-create participants
        actors = [e for e in result.elements if e.element_type == ElementType.ACTOR]
        assert len(actors) == 3
        
        participant_names = [a.name for a in actors]
        assert "Alice" in participant_names
        assert "Bob" in participant_names
        assert "Charlie" in participant_names