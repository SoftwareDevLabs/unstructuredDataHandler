"""
Database package for diagram parsing.

This package provides database models and utilities for storing and querying
parsed diagram information.
"""

from .models import (
    DiagramRecord,
    ElementRecord, 
    RelationshipRecord,
    DiagramDatabase
)

from .utils import (
    DiagramQueryBuilder,
    export_diagram_to_json,
    export_elements_to_csv,
    get_diagram_statistics,
    find_orphaned_elements,
    find_circular_dependencies,
    get_element_dependencies,
    merge_diagrams,
    validate_diagram_integrity
)

__all__ = [
    'DiagramRecord',
    'ElementRecord',
    'RelationshipRecord', 
    'DiagramDatabase',
    'DiagramQueryBuilder',
    'export_diagram_to_json',
    'export_elements_to_csv',
    'get_diagram_statistics',
    'find_orphaned_elements',
    'find_circular_dependencies',
    'get_element_dependencies',
    'merge_diagrams',
    'validate_diagram_integrity'
]