"""
Database utilities for diagram parsing operations.

This module provides utility functions for working with the diagram database,
including import/export, querying, and data manipulation functions.
"""

from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import json
import csv
from .models import DiagramDatabase, DiagramRecord, ElementRecord, RelationshipRecord


class DiagramQueryBuilder:
    """Helper class for building complex database queries."""
    
    def __init__(self, db: DiagramDatabase):
        self.db = db
        self._filters = []
        self._joins = []
        self._select_fields = []
    
    def filter_by_diagram_type(self, diagram_type: str):
        """Filter by diagram type."""
        self._filters.append(f"diagrams.diagram_type = '{diagram_type}'")
        return self
    
    def filter_by_element_type(self, element_type: str):
        """Filter by element type."""
        self._joins.append("JOIN elements ON diagrams.id = elements.diagram_id")
        self._filters.append(f"elements.element_type = '{element_type}'")
        return self
    
    def filter_by_relationship_type(self, relationship_type: str):
        """Filter by relationship type."""
        self._joins.append("JOIN relationships ON diagrams.id = relationships.diagram_id")
        self._filters.append(f"relationships.relationship_type = '{relationship_type}'")
        return self
    
    def build_query(self) -> str:
        """Build the SQL query string."""
        base_query = "SELECT DISTINCT diagrams.* FROM diagrams"
        
        if self._joins:
            base_query += " " + " ".join(set(self._joins))
        
        if self._filters:
            base_query += " WHERE " + " AND ".join(self._filters)
        
        return base_query


def export_diagram_to_json(db: DiagramDatabase, diagram_id: int) -> Dict[str, Any]:
    """Export a complete diagram to JSON format."""
    diagram = db.get_diagram(diagram_id)
    if not diagram:
        raise ValueError(f"Diagram with ID {diagram_id} not found")
    
    elements = db.get_elements(diagram_id)
    relationships = db.get_relationships(diagram_id)
    
    return {
        'diagram': {
            'id': diagram.id,
            'source_file': diagram.source_file,
            'diagram_type': diagram.diagram_type,
            'created_at': diagram.created_at.isoformat() if diagram.created_at else None,
            'updated_at': diagram.updated_at.isoformat() if diagram.updated_at else None,
            'metadata': diagram.metadata,
            'tags': diagram.tags
        },
        'elements': [
            {
                'id': elem.id,
                'element_id': elem.element_id,
                'element_type': elem.element_type,
                'name': elem.name,
                'properties': elem.properties,
                'position': elem.position,
                'tags': elem.tags
            }
            for elem in elements
        ],
        'relationships': [
            {
                'id': rel.id,
                'relationship_id': rel.relationship_id,
                'source_element_id': rel.source_element_id,
                'target_element_id': rel.target_element_id,
                'relationship_type': rel.relationship_type,
                'properties': rel.properties,
                'tags': rel.tags
            }
            for rel in relationships
        ]
    }


def export_elements_to_csv(db: DiagramDatabase, diagram_id: int, output_path: Union[str, Path]):
    """Export diagram elements to CSV file."""
    elements = db.get_elements(diagram_id)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'element_id', 'element_type', 'name', 'properties', 
            'position', 'tags'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for element in elements:
            writer.writerow({
                'element_id': element.element_id,
                'element_type': element.element_type,
                'name': element.name,
                'properties': json.dumps(element.properties),
                'position': json.dumps(element.position) if element.position else '',
                'tags': json.dumps(element.tags)
            })


def get_diagram_statistics(db: DiagramDatabase, diagram_id: int) -> Dict[str, Any]:
    """Get statistics for a diagram."""
    elements = db.get_elements(diagram_id)
    relationships = db.get_relationships(diagram_id)
    
    # Element type counts
    element_type_counts = {}
    for element in elements:
        element_type_counts[element.element_type] = element_type_counts.get(element.element_type, 0) + 1
    
    # Relationship type counts
    relationship_type_counts = {}
    for relationship in relationships:
        relationship_type_counts[relationship.relationship_type] = relationship_type_counts.get(relationship.relationship_type, 0) + 1
    
    # Tag frequency
    all_tags = []
    for element in elements:
        all_tags.extend(element.tags)
    for relationship in relationships:
        all_tags.extend(relationship.tags)
    
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    return {
        'total_elements': len(elements),
        'total_relationships': len(relationships),
        'element_type_counts': element_type_counts,
        'relationship_type_counts': relationship_type_counts,
        'tag_counts': tag_counts,
        'unique_tags': len(tag_counts)
    }


def find_orphaned_elements(db: DiagramDatabase, diagram_id: int) -> List[ElementRecord]:
    """Find elements that have no relationships."""
    elements = db.get_elements(diagram_id)
    relationships = db.get_relationships(diagram_id)
    
    # Get all element IDs that are in relationships
    connected_elements = set()
    for rel in relationships:
        connected_elements.add(rel.source_element_id)
        connected_elements.add(rel.target_element_id)
    
    # Find elements not in any relationship
    orphaned = []
    for element in elements:
        if element.element_id not in connected_elements:
            orphaned.append(element)
    
    return orphaned


def find_circular_dependencies(db: DiagramDatabase, diagram_id: int) -> List[List[str]]:
    """Find circular dependencies in relationships."""
    relationships = db.get_relationships(diagram_id)
    
    # Build adjacency list
    graph = {}
    for rel in relationships:
        if rel.source_element_id not in graph:
            graph[rel.source_element_id] = []
        graph[rel.source_element_id].append(rel.target_element_id)
    
    # Find cycles using DFS
    def find_cycles_dfs(node, path, visited, cycles):
        if node in path:
            # Found a cycle
            cycle_start = path.index(node)
            cycle = path[cycle_start:] + [node]
            cycles.append(cycle)
            return
        
        if node in visited:
            return
        
        visited.add(node)
        path.append(node)
        
        if node in graph:
            for neighbor in graph[node]:
                find_cycles_dfs(neighbor, path, visited, cycles)
        
        path.pop()
    
    cycles = []
    visited = set()
    
    for node in graph:
        if node not in visited:
            find_cycles_dfs(node, [], visited, cycles)
    
    return cycles


def get_element_dependencies(db: DiagramDatabase, diagram_id: int, element_id: str) -> Dict[str, List[str]]:
    """Get dependencies for a specific element."""
    relationships = db.get_relationships(diagram_id)
    
    dependencies = {
        'depends_on': [],  # Elements this element depends on
        'depended_by': []  # Elements that depend on this element
    }
    
    for rel in relationships:
        if rel.source_element_id == element_id:
            dependencies['depends_on'].append(rel.target_element_id)
        elif rel.target_element_id == element_id:
            dependencies['depended_by'].append(rel.source_element_id)
    
    return dependencies


def merge_diagrams(db: DiagramDatabase, diagram_ids: List[int], new_source_file: str) -> int:
    """Merge multiple diagrams into a new diagram."""
    from ..base_parser import ParsedDiagram, DiagramType
    
    # Create new merged diagram
    merged_diagram = ParsedDiagram(
        diagram_type=DiagramType.PLANTUML,  # Default type
        source_file=new_source_file,
        metadata={'merged_from': diagram_ids},
        tags=['merged']
    )
    
    element_id_mapping = {}  # Map old IDs to new IDs to avoid conflicts
    id_counter = 1
    
    # Collect all elements
    for diagram_id in diagram_ids:
        elements = db.get_elements(diagram_id)
        for element in elements:
            # Create unique ID for merged diagram
            new_id = f"elem_{id_counter}"
            element_id_mapping[f"{diagram_id}_{element.element_id}"] = new_id
            id_counter += 1
            
            # Add element to merged diagram
            from ..base_parser import DiagramElement, ElementType
            merged_element = DiagramElement(
                id=new_id,
                element_type=ElementType(element.element_type),
                name=element.name,
                properties=element.properties,
                position=element.position,
                tags=element.tags + [f"from_diagram_{diagram_id}"]
            )
            merged_diagram.elements.append(merged_element)
    
    # Collect all relationships
    for diagram_id in diagram_ids:
        relationships = db.get_relationships(diagram_id)
        for relationship in relationships:
            source_key = f"{diagram_id}_{relationship.source_element_id}"
            target_key = f"{diagram_id}_{relationship.target_element_id}"
            
            # Only add relationship if both elements exist in the merged diagram
            if source_key in element_id_mapping and target_key in element_id_mapping:
                from ..base_parser import DiagramRelationship
                merged_rel = DiagramRelationship(
                    id=f"rel_{len(merged_diagram.relationships) + 1}",
                    source_id=element_id_mapping[source_key],
                    target_id=element_id_mapping[target_key],
                    relationship_type=relationship.relationship_type,
                    properties=relationship.properties,
                    tags=relationship.tags + [f"from_diagram_{diagram_id}"]
                )
                merged_diagram.relationships.append(merged_rel)
    
    # Store merged diagram
    return db.store_diagram(merged_diagram)


def validate_diagram_integrity(db: DiagramDatabase, diagram_id: int) -> Dict[str, Any]:
    """Validate diagram integrity and return issues found."""
    elements = db.get_elements(diagram_id)
    relationships = db.get_relationships(diagram_id)
    
    issues = {
        'missing_elements': [],
        'duplicate_element_ids': [],
        'orphaned_elements': [],
        'circular_dependencies': [],
        'invalid_relationships': []
    }
    
    # Check for missing elements referenced in relationships
    element_ids = {elem.element_id for elem in elements}
    for rel in relationships:
        if rel.source_element_id not in element_ids:
            issues['missing_elements'].append(rel.source_element_id)
        if rel.target_element_id not in element_ids:
            issues['missing_elements'].append(rel.target_element_id)
    
    # Check for duplicate element IDs
    seen_ids = set()
    for elem in elements:
        if elem.element_id in seen_ids:
            issues['duplicate_element_ids'].append(elem.element_id)
        else:
            seen_ids.add(elem.element_id)
    
    # Find orphaned elements
    issues['orphaned_elements'] = [elem.element_id for elem in find_orphaned_elements(db, diagram_id)]
    
    # Find circular dependencies
    issues['circular_dependencies'] = find_circular_dependencies(db, diagram_id)
    
    # Check for self-referencing relationships
    for rel in relationships:
        if rel.source_element_id == rel.target_element_id:
            issues['invalid_relationships'].append({
                'relationship_id': rel.relationship_id,
                'issue': 'self_reference'
            })
    
    return issues