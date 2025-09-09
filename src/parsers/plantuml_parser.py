"""
PlantUML parser for extracting diagram information.

This parser handles PlantUML format files (.puml, .plantuml) and extracts
classes, relationships, and other diagram elements.
"""

import re
from typing import List, Dict, Any, Optional
from .base_parser import BaseParser, ParsedDiagram, DiagramElement, DiagramRelationship
from .base_parser import DiagramType, ElementType, ParseError


class PlantUMLParser(BaseParser):
    """Parser for PlantUML diagram files."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.puml', '.plantuml', '.pu']
    
    @property
    def diagram_type(self) -> DiagramType:
        return DiagramType.PLANTUML
    
    def parse(self, content: str, source_file: str = "") -> ParsedDiagram:
        """Parse PlantUML content and extract diagram information."""
        try:
            diagram = ParsedDiagram(
                diagram_type=self.diagram_type,
                source_file=source_file
            )
            
            # Clean content - remove comments and normalize whitespace
            cleaned_content = self._clean_content(content)
            
            # Extract metadata (title, skinparam, etc.)
            diagram.metadata = self._extract_metadata(cleaned_content)
            
            # Extract elements (classes, interfaces, components, etc.)
            diagram.elements = self._extract_elements(cleaned_content)
            
            # Extract relationships (associations, inheritance, etc.)
            diagram.relationships = self._extract_relationships(cleaned_content)
            
            # Extract global tags
            diagram.tags = self._extract_global_tags(cleaned_content)
            
            return diagram
            
        except Exception as e:
            raise ParseError(f"Failed to parse PlantUML content: {str(e)}")
    
    def _clean_content(self, content: str) -> str:
        """Clean content by removing comments and normalizing whitespace."""
        # Remove multi-line comments first (PlantUML uses /' comment '/ format)
        content = re.sub(r"/\'.*?'/", "", content, flags=re.DOTALL)
        
        # Remove single-line comments
        content = re.sub(r"'.*$", "", content, flags=re.MULTILINE)
        
        # Normalize whitespace but preserve line structure
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata like title, skinparam, etc."""
        metadata = {}
        
        # Extract title
        title_match = re.search(r'title\s+([^\n\r]+)', content, re.IGNORECASE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        # Extract skinparam settings
        skinparams = re.findall(r'skinparam\s+(\w+)\s+([^\n\r]+)', content, re.IGNORECASE)
        if skinparams:
            metadata['skinparams'] = {param: value.strip() for param, value in skinparams}
        
        # Extract notes
        notes = re.findall(r'note\s+(?:left|right|top|bottom|as\s+\w+)\s*:\s*([^\n\r]+)', 
                          content, re.IGNORECASE)
        if notes:
            metadata['notes'] = [note.strip() for note in notes]
        
        return metadata
    
    def _extract_elements(self, content: str) -> List[DiagramElement]:
        """Extract diagram elements (classes, interfaces, etc.)."""
        elements = []
        
        # Class definitions
        class_pattern = r'class\s+(\w+)(?:\s*<<(.+?)>>)?\s*(?:\{(.*?)\})?'
        for match in re.finditer(class_pattern, content, re.IGNORECASE | re.DOTALL):
            name = match.group(1)
            stereotype = match.group(2) if match.group(2) else None
            body = match.group(3) if match.group(3) else ""
            
            properties = self._parse_class_body(body)
            if stereotype:
                properties['stereotype'] = stereotype.strip()
            
            element = DiagramElement(
                id=name,
                element_type=ElementType.CLASS,
                name=name,
                properties=properties,
                tags=self._extract_element_tags(name, content)
            )
            elements.append(element)
        
        # Interface definitions
        interface_pattern = r'interface\s+(\w+)(?:\s*<<(.+?)>>)?\s*(?:\{(.*?)\})?'
        for match in re.finditer(interface_pattern, content, re.IGNORECASE | re.DOTALL):
            name = match.group(1)
            stereotype = match.group(2) if match.group(2) else None
            body = match.group(3) if match.group(3) else ""
            
            properties = self._parse_class_body(body)
            if stereotype:
                properties['stereotype'] = stereotype.strip()
            
            element = DiagramElement(
                id=name,
                element_type=ElementType.INTERFACE,
                name=name,
                properties=properties,
                tags=self._extract_element_tags(name, content)
            )
            elements.append(element)
        
        # Actor definitions
        actor_pattern = r'actor\s+(\w+)(?:\s+as\s+(\w+))?'
        for match in re.finditer(actor_pattern, content, re.IGNORECASE):
            name = match.group(1)
            alias = match.group(2) if match.group(2) else name
            
            element = DiagramElement(
                id=alias,
                element_type=ElementType.ACTOR,
                name=name,
                properties={'alias': alias} if alias != name else {},
                tags=self._extract_element_tags(name, content)
            )
            elements.append(element)
        
        # Component definitions
        component_pattern = r'component\s+(\w+)(?:\s+as\s+(\w+))?'
        for match in re.finditer(component_pattern, content, re.IGNORECASE):
            name = match.group(1)
            alias = match.group(2) if match.group(2) else name
            
            element = DiagramElement(
                id=alias,
                element_type=ElementType.COMPONENT,
                name=name,
                properties={'alias': alias} if alias != name else {},
                tags=self._extract_element_tags(name, content)
            )
            elements.append(element)
        
        return elements
    
    def _parse_class_body(self, body: str) -> Dict[str, Any]:
        """Parse class body to extract methods and attributes."""
        properties = {'methods': [], 'attributes': []}
        
        if not body:
            return properties
        
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        
        for line in lines:
            # Skip empty lines and separators
            if not line or line in ['--', '..', '==']:
                continue
            
            # Method pattern (has parentheses)
            if '(' in line and ')' in line:
                properties['methods'].append(line)
            else:
                # Attribute pattern
                properties['attributes'].append(line)
        
        return properties
    
    def _extract_relationships(self, content: str) -> List[DiagramRelationship]:
        """Extract relationships between elements."""
        relationships = []
        
        # Common relationship patterns
        patterns = [
            # Inheritance: A --|> B, A <|-- B
            (r'(\w+)\s*<\|--\s*(\w+)', 'inheritance', 'reverse'),
            (r'(\w+)\s*--\|>\s*(\w+)', 'inheritance', 'normal'),
            
            # Composition: A *-- B, B --* A
            (r'(\w+)\s*\*--\s*(\w+)', 'composition', 'normal'),
            (r'(\w+)\s*--\*\s*(\w+)', 'composition', 'reverse'),
            
            # Aggregation: A o-- B, B --o A
            (r'(\w+)\s*o--\s*(\w+)', 'aggregation', 'normal'),
            (r'(\w+)\s*--o\s*(\w+)', 'aggregation', 'reverse'),
            
            # Association: A -- B, A --> B
            (r'(\w+)\s*-->\s*(\w+)', 'association', 'normal'),
            (r'(\w+)\s*<--\s*(\w+)', 'association', 'reverse'),
            (r'\b(?!o|O|\*)\w+\b\s*--\s*\b\w+\b', 'association', 'normal'),
            
            # Dependency: A ..> B, A <.. B
            (r'(\w+)\s*\.\.>\s*(\w+)', 'dependency', 'normal'),
            (r'(\w+)\s*<\.\.\s*(\w+)', 'dependency', 'reverse'),
        ]
        
        rel_id = 1
        for pattern, rel_type, direction in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                source = match.group(1) if direction == 'normal' else match.group(2)
                target = match.group(2) if direction == 'normal' else match.group(1)
                
                relationship = DiagramRelationship(
                    id=f"rel_{rel_id}",
                    source_id=source,
                    target_id=target,
                    relationship_type=rel_type,
                    properties={'direction': direction},
                    tags=[]
                )
                relationships.append(relationship)
                rel_id += 1
        
        return relationships
    
    def _extract_element_tags(self, element_name: str, content: str) -> List[str]:
        """Extract tags specific to an element."""
        tags = []
        
        # Look for tagged annotations near the element
        tag_pattern = rf'{re.escape(element_name)}\s*:\s*#(\w+)'
        for match in re.finditer(tag_pattern, content, re.IGNORECASE):
            tags.append(match.group(1))
        
        return tags
    
    def _extract_global_tags(self, content: str) -> List[str]:
        """Extract global tags from the diagram."""
        tags = []
        
        # Look for global tag annotations
        tag_pattern = r'#(\w+)'
        for match in re.finditer(tag_pattern, content):
            tag = match.group(1)
            if tag not in tags:
                tags.append(tag)
        
        return tags