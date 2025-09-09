import unittest
import tempfile
import os
from src.parsers.database.models import DiagramDatabase
from src.parsers.database.utils import DiagramQueryBuilder, find_circular_dependencies, get_element_dependencies, merge_diagrams
from src.parsers.base_parser import ParsedDiagram, DiagramElement, DiagramRelationship, DiagramType, ElementType

class TestDatabaseUtilsCoverage(unittest.TestCase):
    """
    Test suite to improve coverage for the database utils module.
    """

    def setUp(self):
        """Set up a temporary database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = DiagramDatabase(self.temp_db.name)

    def tearDown(self):
        """Clean up the temporary database."""
        os.unlink(self.temp_db.name)

    def test_diagram_query_builder(self):
        """
        Test the DiagramQueryBuilder class.
        """
        builder = DiagramQueryBuilder(self.db)
        query = builder.filter_by_diagram_type("plantuml").filter_by_element_type("class").build_query()

        self.assertIn("diagrams.diagram_type = 'plantuml'", query)
        self.assertIn("elements.element_type = 'class'", query)
        self.assertIn("JOIN elements ON diagrams.id = elements.diagram_id", query)

    def test_find_circular_dependencies(self):
        """
        Test the find_circular_dependencies function.
        """
        elements = [
            DiagramElement(id="A", element_type=ElementType.CLASS, name="A"),
            DiagramElement(id="B", element_type=ElementType.CLASS, name="B"),
            DiagramElement(id="C", element_type=ElementType.CLASS, name="C"),
        ]
        relationships = [
            DiagramRelationship(id="1", source_id="A", target_id="B", relationship_type="dependency"),
            DiagramRelationship(id="2", source_id="B", target_id="C", relationship_type="dependency"),
            DiagramRelationship(id="3", source_id="C", target_id="A", relationship_type="dependency"),
        ]
        diagram = ParsedDiagram(diagram_type=DiagramType.PLANTUML, source_file="test.puml", elements=elements, relationships=relationships)
        diagram_id = self.db.store_diagram(diagram)

        cycles = find_circular_dependencies(self.db, diagram_id)
        self.assertEqual(len(cycles), 1)
        self.assertEqual(cycles[0], ['A', 'B', 'C', 'A'])

    def test_get_element_dependencies(self):
        """
        Test the get_element_dependencies function.
        """
        elements = [
            DiagramElement(id="A", element_type=ElementType.CLASS, name="A"),
            DiagramElement(id="B", element_type=ElementType.CLASS, name="B"),
            DiagramElement(id="C", element_type=ElementType.CLASS, name="C"),
        ]
        relationships = [
            DiagramRelationship(id="1", source_id="A", target_id="B", relationship_type="dependency"),
            DiagramRelationship(id="2", source_id="C", target_id="A", relationship_type="dependency"),
        ]
        diagram = ParsedDiagram(diagram_type=DiagramType.PLANTUML, source_file="test.puml", elements=elements, relationships=relationships)
        diagram_id = self.db.store_diagram(diagram)

        dependencies = get_element_dependencies(self.db, diagram_id, "A")
        self.assertEqual(dependencies['depends_on'], ['B'])
        self.assertEqual(dependencies['depended_by'], ['C'])

    def test_merge_diagrams(self):
        """
        Test the merge_diagrams function.
        """
        # Diagram 1
        d1_elements = [DiagramElement(id="A", element_type=ElementType.CLASS, name="A")]
        d1 = ParsedDiagram(diagram_type=DiagramType.PLANTUML, source_file="d1.puml", elements=d1_elements)
        d1_id = self.db.store_diagram(d1)

        # Diagram 2
        d2_elements = [DiagramElement(id="B", element_type=ElementType.CLASS, name="B")]
        d2 = ParsedDiagram(diagram_type=DiagramType.PLANTUML, source_file="d2.puml", elements=d2_elements)
        d2_id = self.db.store_diagram(d2)

        merged_id = merge_diagrams(self.db, [d1_id, d2_id], "merged.puml")

        merged_elements = self.db.get_elements(merged_id)
        self.assertEqual(len(merged_elements), 2)

        names = {e.name for e in merged_elements}
        self.assertIn("A", names)
        self.assertIn("B", names)

if __name__ == '__main__':
    unittest.main()
