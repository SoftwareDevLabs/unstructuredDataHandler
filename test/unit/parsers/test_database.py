"""
Tests for database models and utilities.
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.parsers.database.models import DiagramDatabase, DiagramRecord, ElementRecord, RelationshipRecord
from src.parsers.database.utils import (
    export_diagram_to_json, get_diagram_statistics, find_orphaned_elements,
    validate_diagram_integrity
)
from src.parsers.base_parser import ParsedDiagram, DiagramElement, DiagramRelationship
from src.parsers.base_parser import DiagramType, ElementType


class TestDiagramDatabase:
    """Test DiagramDatabase functionality."""
    
    def setup_method(self):
        """Set up test database."""
        # Use temporary file for test database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = DiagramDatabase(self.temp_db.name)
    
    def teardown_method(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization and schema creation."""
        # Database should be created and initialized
        assert os.path.exists(self.temp_db.name)
        
        # Should be able to get empty diagrams list
        diagrams = self.db.get_all_diagrams()
        assert diagrams == []
    
    def test_store_and_retrieve_diagram(self):
        """Test storing and retrieving a parsed diagram."""
        # Create test diagram
        element = DiagramElement(
            id="test_element",
            element_type=ElementType.CLASS,
            name="TestClass",
            properties={"visibility": "public"},
            position={"x": 10.0, "y": 20.0},
            tags=["important"]
        )
        
        relationship = DiagramRelationship(
            id="test_rel",
            source_id="test_element",
            target_id="other_element",
            relationship_type="association",
            properties={"multiplicity": "1..*"},
            tags=["key_relation"]
        )
        
        diagram = ParsedDiagram(
            diagram_type=DiagramType.PLANTUML,
            source_file="test.puml",
            elements=[element],
            relationships=[relationship],
            metadata={"title": "Test Diagram"},
            tags=["test", "example"]
        )
        
        # Store diagram
        diagram_id = self.db.store_diagram(diagram)
        assert diagram_id > 0
        
        # Retrieve diagram
        stored_diagram = self.db.get_diagram(diagram_id)
        assert stored_diagram is not None
        assert stored_diagram.source_file == "test.puml"
        assert stored_diagram.diagram_type == "plantuml"
        assert stored_diagram.metadata["title"] == "Test Diagram"
        assert "test" in stored_diagram.tags
        
        # Retrieve elements
        elements = self.db.get_elements(diagram_id)
        assert len(elements) == 1
        assert elements[0].element_id == "test_element"
        assert elements[0].name == "TestClass"
        assert elements[0].properties["visibility"] == "public"
        
        # Retrieve relationships
        relationships = self.db.get_relationships(diagram_id)
        assert len(relationships) == 1
        assert relationships[0].relationship_id == "test_rel"
        assert relationships[0].source_element_id == "test_element"
        assert relationships[0].relationship_type == "association"
    
    def test_search_elements_by_type(self):
        """Test searching elements by type."""
        # Create and store test diagram
        element1 = DiagramElement(
            id="class1",
            element_type=ElementType.CLASS,
            name="TestClass"
        )
        
        element2 = DiagramElement(
            id="interface1",
            element_type=ElementType.INTERFACE,
            name="TestInterface"
        )
        
        diagram = ParsedDiagram(
            diagram_type=DiagramType.PLANTUML,
            source_file="test.puml",
            elements=[element1, element2]
        )
        
        diagram_id = self.db.store_diagram(diagram)
        
        # Search for classes
        class_elements = self.db.search_elements_by_type("class")
        assert len(class_elements) == 1
        assert class_elements[0].name == "TestClass"
        
        # Search for interfaces
        interface_elements = self.db.search_elements_by_type("interface")
        assert len(interface_elements) == 1
        assert interface_elements[0].name == "TestInterface"
    
    def test_search_by_tags(self):
        """Test searching by tags."""
        # Create elements with tags
        element = DiagramElement(
            id="tagged_element",
            element_type=ElementType.CLASS,
            name="TaggedClass",
            tags=["important", "api"]
        )
        
        relationship = DiagramRelationship(
            id="tagged_rel",
            source_id="a",
            target_id="b",
            relationship_type="association",
            tags=["core", "api"]
        )
        
        diagram = ParsedDiagram(
            diagram_type=DiagramType.PLANTUML,
            source_file="test.puml",
            elements=[element],
            relationships=[relationship],
            tags=["system", "core"]
        )
        
        diagram_id = self.db.store_diagram(diagram)
        
        # Search by tag
        results = self.db.search_by_tags(["api"])
        
        # Should find both element and relationship
        assert len(results["elements"]) == 1
        assert len(results["relationships"]) == 1
        assert results["elements"][0]["name"] == "TaggedClass"
        
        # Search by diagram tag
        core_results = self.db.search_by_tags(["core"])
        assert len(core_results["diagrams"]) == 1
        assert len(core_results["relationships"]) == 1
    
    def test_delete_diagram(self):
        """Test deleting a diagram."""
        # Create and store test diagram
        element = DiagramElement(
            id="test_element",
            element_type=ElementType.CLASS,
            name="TestClass"
        )
        
        diagram = ParsedDiagram(
            diagram_type=DiagramType.PLANTUML,
            source_file="test.puml",
            elements=[element]
        )
        
        diagram_id = self.db.store_diagram(diagram)
        
        # Verify diagram exists
        assert self.db.get_diagram(diagram_id) is not None
        assert len(self.db.get_elements(diagram_id)) == 1
        
        # Delete diagram
        success = self.db.delete_diagram(diagram_id)
        assert success is True
        
        # Verify diagram is deleted
        assert self.db.get_diagram(diagram_id) is None
        assert len(self.db.get_elements(diagram_id)) == 0


class TestDatabaseUtils:
    """Test database utility functions."""
    
    def setup_method(self):
        """Set up test database with sample data."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = DiagramDatabase(self.temp_db.name)
        
        # Create sample diagram
        elements = [
            DiagramElement(
                id="class1",
                element_type=ElementType.CLASS,
                name="ClassA",
                tags=["important"]
            ),
            DiagramElement(
                id="class2",
                element_type=ElementType.CLASS,
                name="ClassB"
            ),
            DiagramElement(
                id="orphan",
                element_type=ElementType.CLASS,
                name="OrphanClass"
            )
        ]
        
        relationships = [
            DiagramRelationship(
                id="rel1",
                source_id="class1",
                target_id="class2",
                relationship_type="inheritance"
            )
        ]
        
        diagram = ParsedDiagram(
            diagram_type=DiagramType.PLANTUML,
            source_file="test.puml",
            elements=elements,
            relationships=relationships,
            tags=["test"]
        )
        
        self.diagram_id = self.db.store_diagram(diagram)
    
    def teardown_method(self):
        """Clean up test database."""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_export_diagram_to_json(self):
        """Test exporting diagram to JSON."""
        json_data = export_diagram_to_json(self.db, self.diagram_id)
        
        assert "diagram" in json_data
        assert "elements" in json_data
        assert "relationships" in json_data
        
        # Check diagram data
        diagram_data = json_data["diagram"]
        assert diagram_data["source_file"] == "test.puml"
        assert diagram_data["diagram_type"] == "plantuml"
        
        # Check elements
        assert len(json_data["elements"]) == 3
        class_names = [elem["name"] for elem in json_data["elements"]]
        assert "ClassA" in class_names
        assert "ClassB" in class_names
        assert "OrphanClass" in class_names
        
        # Check relationships
        assert len(json_data["relationships"]) == 1
        assert json_data["relationships"][0]["relationship_type"] == "inheritance"
    
    def test_get_diagram_statistics(self):
        """Test getting diagram statistics."""
        stats = get_diagram_statistics(self.db, self.diagram_id)
        
        assert stats["total_elements"] == 3
        assert stats["total_relationships"] == 1
        assert stats["element_type_counts"]["class"] == 3
        assert stats["relationship_type_counts"]["inheritance"] == 1
        assert stats["tag_counts"]["important"] == 1
        assert stats["unique_tags"] == 1
    
    def test_find_orphaned_elements(self):
        """Test finding orphaned elements."""
        orphaned = find_orphaned_elements(self.db, self.diagram_id)
        
        assert len(orphaned) == 1
        assert orphaned[0].element_id == "orphan"
        assert orphaned[0].name == "OrphanClass"
    
    def test_validate_diagram_integrity(self):
        """Test diagram integrity validation."""
        issues = validate_diagram_integrity(self.db, self.diagram_id)
        
        # Should find orphaned element
        assert "orphan" in issues["orphaned_elements"]
        
        # Should not find missing elements (all referenced elements exist)
        assert len(issues["missing_elements"]) == 0
        
        # Should not find duplicate IDs
        assert len(issues["duplicate_element_ids"]) == 0
    
    def test_export_elements_to_csv(self, tmp_path):
        """Test exporting elements to CSV."""
        from src.parsers.database.utils import export_elements_to_csv
        
        csv_file = tmp_path / "elements.csv"
        export_elements_to_csv(self.db, self.diagram_id, csv_file)
        
        # Check if file was created
        assert csv_file.exists()
        
        # Read and verify content
        content = csv_file.read_text()
        assert "element_id" in content  # Header
        assert "ClassA" in content
        assert "ClassB" in content
        assert "OrphanClass" in content
    
    def test_export_nonexistent_diagram(self):
        """Test exporting nonexistent diagram."""
        with pytest.raises(ValueError) as exc_info:
            export_diagram_to_json(self.db, 99999)
        
        assert "not found" in str(exc_info.value)