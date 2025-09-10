"""
Database models for storing parsed diagram information.

This module defines data models and database schema for storing
extracted diagram elements, relationships, and metadata.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import json
import sqlite3
from pathlib import Path


@dataclass
class DiagramRecord:
    """Database record for a parsed diagram."""
    id: Optional[int] = None
    source_file: str = ""
    diagram_type: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class ElementRecord:
    """Database record for a diagram element."""
    id: Optional[int] = None
    diagram_id: int = 0
    element_id: str = ""
    element_type: str = ""
    name: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    position: Optional[Dict[str, float]] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class RelationshipRecord:
    """Database record for a diagram relationship."""
    id: Optional[int] = None
    diagram_id: int = 0
    relationship_id: str = ""
    source_element_id: str = ""
    target_element_id: str = ""
    relationship_type: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


class DiagramDatabase:
    """SQLite database for storing parsed diagram information."""
    
    def __init__(self, db_path: Union[str, Path] = "diagrams.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS diagrams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_file TEXT NOT NULL,
                    diagram_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    tags TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS elements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    diagram_id INTEGER NOT NULL,
                    element_id TEXT NOT NULL,
                    element_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    properties TEXT,
                    position TEXT,
                    tags TEXT,
                    FOREIGN KEY (diagram_id) REFERENCES diagrams (id) ON DELETE CASCADE
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    diagram_id INTEGER NOT NULL,
                    relationship_id TEXT NOT NULL,
                    source_element_id TEXT NOT NULL,
                    target_element_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    properties TEXT,
                    tags TEXT,
                    FOREIGN KEY (diagram_id) REFERENCES diagrams (id) ON DELETE CASCADE
                )
            ''')
            
            # Create indexes for better query performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_elements_diagram_id ON elements (diagram_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_elements_type ON elements (element_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_relationships_diagram_id ON relationships (diagram_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships (relationship_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships (source_element_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships (target_element_id)')
    
    def store_diagram(self, parsed_diagram) -> int:
        """
        Store a parsed diagram in the database.
        
        Args:
            parsed_diagram: ParsedDiagram object to store
            
        Returns:
            Database ID of the stored diagram
        """
        from ..base_parser import ParsedDiagram
        
        with sqlite3.connect(self.db_path) as conn:
            # Insert diagram record
            cursor = conn.execute('''
                INSERT INTO diagrams (source_file, diagram_type, metadata, tags)
                VALUES (?, ?, ?, ?)
            ''', (
                parsed_diagram.source_file,
                parsed_diagram.diagram_type.value,
                json.dumps(parsed_diagram.metadata),
                json.dumps(parsed_diagram.tags)
            ))
            
            diagram_id = cursor.lastrowid
            
            # Insert elements
            for element in parsed_diagram.elements:
                conn.execute('''
                    INSERT INTO elements (
                        diagram_id, element_id, element_type, name, 
                        properties, position, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    diagram_id,
                    element.id,
                    element.element_type.value,
                    element.name,
                    json.dumps(element.properties),
                    json.dumps(element.position) if element.position else None,
                    json.dumps(element.tags)
                ))
            
            # Insert relationships
            for relationship in parsed_diagram.relationships:
                conn.execute('''
                    INSERT INTO relationships (
                        diagram_id, relationship_id, source_element_id, 
                        target_element_id, relationship_type, properties, tags
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    diagram_id,
                    relationship.id,
                    relationship.source_id,
                    relationship.target_id,
                    relationship.relationship_type,
                    json.dumps(relationship.properties),
                    json.dumps(relationship.tags)
                ))
            
            conn.commit()
            return diagram_id
    
    def get_diagram(self, diagram_id: int) -> Optional[DiagramRecord]:
        """Retrieve a diagram record by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM diagrams WHERE id = ?
            ''', (diagram_id,))
            
            row = cursor.fetchone()
            if row:
                return DiagramRecord(
                    id=row['id'],
                    source_file=row['source_file'],
                    diagram_type=row['diagram_type'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                    tags=json.loads(row['tags']) if row['tags'] else []
                )
            return None
    
    def get_elements(self, diagram_id: int) -> List[ElementRecord]:
        """Retrieve all elements for a diagram."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM elements WHERE diagram_id = ?
            ''', (diagram_id,))
            
            elements = []
            for row in cursor.fetchall():
                elements.append(ElementRecord(
                    id=row['id'],
                    diagram_id=row['diagram_id'],
                    element_id=row['element_id'],
                    element_type=row['element_type'],
                    name=row['name'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    position=json.loads(row['position']) if row['position'] else None,
                    tags=json.loads(row['tags']) if row['tags'] else []
                ))
            
            return elements
    
    def get_relationships(self, diagram_id: int) -> List[RelationshipRecord]:
        """Retrieve all relationships for a diagram."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM relationships WHERE diagram_id = ?
            ''', (diagram_id,))
            
            relationships = []
            for row in cursor.fetchall():
                relationships.append(RelationshipRecord(
                    id=row['id'],
                    diagram_id=row['diagram_id'],
                    relationship_id=row['relationship_id'],
                    source_element_id=row['source_element_id'],
                    target_element_id=row['target_element_id'],
                    relationship_type=row['relationship_type'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    tags=json.loads(row['tags']) if row['tags'] else []
                ))
            
            return relationships
    
    def search_elements_by_type(self, element_type: str) -> List[ElementRecord]:
        """Search elements by type across all diagrams."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM elements WHERE element_type = ?
            ''', (element_type,))
            
            elements = []
            for row in cursor.fetchall():
                elements.append(ElementRecord(
                    id=row['id'],
                    diagram_id=row['diagram_id'],
                    element_id=row['element_id'],
                    element_type=row['element_type'],
                    name=row['name'],
                    properties=json.loads(row['properties']) if row['properties'] else {},
                    position=json.loads(row['position']) if row['position'] else None,
                    tags=json.loads(row['tags']) if row['tags'] else []
                ))
            
            return elements
    
    def search_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Search diagrams, elements, and relationships by tags."""
        results = {'diagrams': [], 'elements': [], 'relationships': []}
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Search diagrams
            for tag in tags:
                cursor = conn.execute('''
                    SELECT * FROM diagrams WHERE tags LIKE ?
                ''', (f'%{tag}%',))
                
                for row in cursor.fetchall():
                    diagram_tags = json.loads(row['tags']) if row['tags'] else []
                    if tag in diagram_tags:
                        results['diagrams'].append({
                            'id': row['id'],
                            'source_file': row['source_file'],
                            'diagram_type': row['diagram_type'],
                            'matching_tag': tag
                        })
            
            # Search elements
            for tag in tags:
                cursor = conn.execute('''
                    SELECT * FROM elements WHERE tags LIKE ?
                ''', (f'%{tag}%',))
                
                for row in cursor.fetchall():
                    element_tags = json.loads(row['tags']) if row['tags'] else []
                    if tag in element_tags:
                        results['elements'].append({
                            'id': row['id'],
                            'diagram_id': row['diagram_id'],
                            'element_id': row['element_id'],
                            'name': row['name'],
                            'element_type': row['element_type'],
                            'matching_tag': tag
                        })
            
            # Search relationships
            for tag in tags:
                cursor = conn.execute('''
                    SELECT * FROM relationships WHERE tags LIKE ?
                ''', (f'%{tag}%',))
                
                for row in cursor.fetchall():
                    rel_tags = json.loads(row['tags']) if row['tags'] else []
                    if tag in rel_tags:
                        results['relationships'].append({
                            'id': row['id'],
                            'diagram_id': row['diagram_id'],
                            'relationship_id': row['relationship_id'],
                            'relationship_type': row['relationship_type'],
                            'matching_tag': tag
                        })
        
        return results
    
    def get_all_diagrams(self) -> List[DiagramRecord]:
        """Retrieve all diagram records."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('SELECT * FROM diagrams ORDER BY created_at DESC')
            
            diagrams = []
            for row in cursor.fetchall():
                diagrams.append(DiagramRecord(
                    id=row['id'],
                    source_file=row['source_file'],
                    diagram_type=row['diagram_type'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None,
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                    tags=json.loads(row['tags']) if row['tags'] else []
                ))
            
            return diagrams
    
    def delete_diagram(self, diagram_id: int) -> bool:
        """Delete a diagram and all its related records."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.execute('DELETE FROM diagrams WHERE id = ?', (diagram_id,))
            conn.commit()
            return cursor.rowcount > 0