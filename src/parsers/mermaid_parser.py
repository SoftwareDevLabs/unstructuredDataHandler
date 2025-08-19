"""
Mermaid parser for extracting diagram information.

This parser handles Mermaid format files (.mmd, .mermaid) and extracts
classes, relationships, and other diagram elements from various Mermaid diagram types.
"""

import re
import json
from typing import List, Dict, Any, Optional
from .base_parser import BaseParser, ParsedDiagram, DiagramElement, DiagramRelationship
from .base_parser import DiagramType, ElementType, ParseError


class MermaidParser(BaseParser):
    """Parser for Mermaid diagram files."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.mmd', '.mermaid']
    
    @property
    def diagram_type(self) -> DiagramType:
        return DiagramType.MERMAID
    
    def parse(self, content: str, source_file: str = "") -> ParsedDiagram:
        """Parse Mermaid content and extract diagram information."""
        try:
            diagram = ParsedDiagram(
                diagram_type=self.diagram_type,
                source_file=source_file
            )
            
            # Clean content
            cleaned_content = self._clean_content(content)
            
            # Determine diagram type
            mermaid_type = self._detect_mermaid_type(cleaned_content)
            diagram.metadata['mermaid_type'] = mermaid_type
            
            # Parse based on diagram type
            if mermaid_type == 'classDiagram':
                self._parse_class_diagram(cleaned_content, diagram)
            elif mermaid_type == 'flowchart' or mermaid_type == 'graph':
                self._parse_flowchart(cleaned_content, diagram)
            elif mermaid_type == 'sequenceDiagram':
                self._parse_sequence_diagram(cleaned_content, diagram)
            elif mermaid_type == 'erDiagram':
                self._parse_er_diagram(cleaned_content, diagram)
            else:
                # Generic parsing for unknown types
                self._parse_generic(cleaned_content, diagram)
            
            # Extract global tags and metadata
            diagram.tags = self._extract_global_tags(cleaned_content)
            diagram.metadata.update(self._extract_metadata(cleaned_content))
            
            return diagram
            
        except Exception as e:
            raise ParseError(f"Failed to parse Mermaid content: {str(e)}")
    
    def _clean_content(self, content: str) -> str:
        """Clean content by removing comments and normalizing whitespace."""
        # Remove comments
        content = re.sub(r'%%.*', '', content)
        
        # Normalize whitespace but preserve line structure
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return '\n'.join(lines)
    
    def _detect_mermaid_type(self, content: str) -> str:
        """Detect the type of Mermaid diagram."""
        first_line = content.split('\n')[0].strip()
        
        if first_line.startswith('classDiagram'):
            return 'classDiagram'
        elif first_line.startswith('sequenceDiagram'):
            return 'sequenceDiagram'
        elif first_line.startswith('erDiagram'):
            return 'erDiagram'
        elif first_line.startswith('flowchart') or first_line.startswith('graph'):
            return first_line.split()[0]
        else:
            return 'unknown'
    
    def _parse_class_diagram(self, content: str, diagram: ParsedDiagram):
        """Parse class diagram specific content."""
        lines = content.split('\n')[1:]  # Skip diagram type line
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Class definition: class ClassName
            class_match = re.match(r'class\s+(\w+)(?:\s*\{([^}]*)\})?', line)
            if class_match:
                class_name = class_match.group(1)
                class_body = class_match.group(2) if class_match.group(2) else ""
                
                properties = self._parse_mermaid_class_body(class_body)
                
                element = DiagramElement(
                    id=class_name,
                    element_type=ElementType.CLASS,
                    name=class_name,
                    properties=properties,
                    tags=[]
                )
                diagram.elements.append(element)
                continue
            
            # Relationship patterns
            self._parse_class_relationships(line, diagram)
    
    def _parse_mermaid_class_body(self, body: str) -> Dict[str, Any]:
        """Parse Mermaid class body."""
        properties = {'methods': [], 'attributes': []}
        
        if not body:
            return properties
        
        lines = [line.strip() for line in body.split('\n') if line.strip()]
        
        for line in lines:
            if '(' in line and ')' in line:
                properties['methods'].append(line)
            else:
                properties['attributes'].append(line)
        
        return properties
    
    def _parse_class_relationships(self, line: str, diagram: ParsedDiagram):
        """Parse class diagram relationships."""
        # Mermaid class relationship patterns
        patterns = [
            # Inheritance: A <|-- B
            (r'(\w+)\s*<\|--\s*(\w+)', 'inheritance'),
            (r'(\w+)\s*--\|>\s*(\w+)', 'inheritance'),
            
            # Composition: A *-- B
            (r'(\w+)\s*\*--\s*(\w+)', 'composition'),
            (r'(\w+)\s*--\*\s*(\w+)', 'composition'),
            
            # Aggregation: A o-- B
            (r'(\w+)\s*o--\s*(\w+)', 'aggregation'),
            (r'(\w+)\s*--o\s*(\w+)', 'aggregation'),
            
            # Association: A -- B
            (r'(\w+)\s*--\s*(\w+)', 'association'),
            (r'(\w+)\s*-->\s*(\w+)', 'association'),
            
            # Dependency: A ..> B
            (r'(\w+)\s*\.\.>\s*(\w+)', 'dependency'),
        ]
        
        for pattern, rel_type in patterns:
            match = re.match(pattern, line)
            if match:
                source = match.group(1)
                target = match.group(2)
                
                relationship = DiagramRelationship(
                    id=f"rel_{len(diagram.relationships) + 1}",
                    source_id=source,
                    target_id=target,
                    relationship_type=rel_type,
                    properties={},
                    tags=[]
                )
                diagram.relationships.append(relationship)
                break
    
    def _parse_flowchart(self, content: str, diagram: ParsedDiagram):
        """Parse flowchart/graph diagram."""
        lines = content.split('\n')[1:]  # Skip diagram type line
        
        # Track created nodes to avoid duplicates
        created_nodes = set()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Node definitions with labels: A[Label] or A(Label) or A{Label}
            node_patterns = [
                (r'(\w+)\[([^\]]+)\]', 'rectangular'),
                (r'(\w+)\(([^)]+)\)', 'rounded'),
                (r'(\w+)\{([^}]+)\}', 'diamond'),
                (r'(\w+)\(\(([^)]+)\)\)', 'circle'),
            ]
            
            for pattern, shape in node_patterns:
                match = re.search(pattern, line)
                if match:
                    node_id = match.group(1)
                    label = match.group(2)
                    
                    if node_id not in created_nodes:
                        element = DiagramElement(
                            id=node_id,
                            element_type=ElementType.COMPONENT,
                            name=label,
                            properties={'shape': shape},
                            tags=[]
                        )
                        diagram.elements.append(element)
                        created_nodes.add(node_id)
            
            # Connection patterns: A --> B or A --- B
            connection_patterns = [
                (r'(\w+)\s*-->\s*(\w+)', 'directed'),
                (r'(\w+)\s*---\s*(\w+)', 'undirected'),
                (r'(\w+)\s*-\.->\s*(\w+)', 'dotted'),
                (r'(\w+)\s*==>\s*(\w+)', 'thick'),
            ]
            
            for pattern, style in connection_patterns:
                match = re.search(pattern, line)
                if match:
                    source = match.group(1)
                    target = match.group(2)
                    
                    # Create nodes if they don't exist (simple node without labels)
                    for node_id in [source, target]:
                        if node_id not in created_nodes:
                            element = DiagramElement(
                                id=node_id,
                                element_type=ElementType.COMPONENT,
                                name=node_id,
                                properties={'shape': 'simple'},
                                tags=[]
                            )
                            diagram.elements.append(element)
                            created_nodes.add(node_id)
                    
                    relationship = DiagramRelationship(
                        id=f"rel_{len(diagram.relationships) + 1}",
                        source_id=source,
                        target_id=target,
                        relationship_type='connection',
                        properties={'style': style},
                        tags=[]
                    )
                    diagram.relationships.append(relationship)
    
    def _parse_sequence_diagram(self, content: str, diagram: ParsedDiagram):
        """Parse sequence diagram."""
        lines = content.split('\n')[1:]  # Skip diagram type line
        
        participants = set()
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Participant declaration
            participant_match = re.match(r'participant\s+(\w+)(?:\s+as\s+(.+))?', line)
            if participant_match:
                participant_id = participant_match.group(1)
                participant_name = participant_match.group(2) if participant_match.group(2) else participant_id
                participants.add(participant_id)
                
                element = DiagramElement(
                    id=participant_id,
                    element_type=ElementType.ACTOR,
                    name=participant_name,
                    properties={},
                    tags=[]
                )
                diagram.elements.append(element)
                continue
            
            # Message patterns: A->>B: message
            message_patterns = [
                (r'(\w+)\s*->>\s*(\w+)\s*:\s*(.+)', 'async_message'),
                (r'(\w+)\s*->\s*(\w+)\s*:\s*(.+)', 'sync_message'),
                (r'(\w+)\s*-->\s*(\w+)\s*:\s*(.+)', 'return_message'),
            ]
            
            for pattern, msg_type in message_patterns:
                match = re.match(pattern, line)
                if match:
                    source = match.group(1)
                    target = match.group(2)
                    message = match.group(3)
                    
                    # Add participants if not already declared
                    for participant in [source, target]:
                        if participant not in participants:
                            participants.add(participant)
                            element = DiagramElement(
                                id=participant,
                                element_type=ElementType.ACTOR,
                                name=participant,
                                properties={},
                                tags=[]
                            )
                            diagram.elements.append(element)
                    
                    relationship = DiagramRelationship(
                        id=f"rel_{len(diagram.relationships) + 1}",
                        source_id=source,
                        target_id=target,
                        relationship_type=msg_type,
                        properties={'message': message},
                        tags=[]
                    )
                    diagram.relationships.append(relationship)
                    break
    
    def _parse_er_diagram(self, content: str, diagram: ParsedDiagram):
        """Parse entity-relationship diagram."""
        lines = content.split('\n')[1:]  # Skip diagram type line
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Entity definition with attributes: ENTITY { attr1 attr2 }
            entity_match = re.match(r'(\w+)\s*\{([^}]*)\}', line)
            if entity_match:
                entity_name = entity_match.group(1)
                attributes_text = entity_match.group(2)
                
                attributes = []
                if attributes_text:
                    attr_lines = [attr.strip() for attr in attributes_text.split('\n') if attr.strip()]
                    for attr_line in attr_lines:
                        if attr_line:  # Skip empty lines
                            attributes.append(attr_line)
                
                element = DiagramElement(
                    id=entity_name,
                    element_type=ElementType.ENTITY,
                    name=entity_name,
                    properties={'attributes': attributes},
                    tags=[]
                )
                diagram.elements.append(element)
                continue
            
            # Entity definition without attributes: ENTITY
            simple_entity_match = re.match(r'^(\w+)$', line)
            if simple_entity_match and not any(rel_pattern in line for rel_pattern in ['||', '}o', 'o{', '--']):
                entity_name = simple_entity_match.group(1)
                
                # Check if entity already exists
                if not any(elem.id == entity_name for elem in diagram.elements):
                    element = DiagramElement(
                        id=entity_name,
                        element_type=ElementType.ENTITY,
                        name=entity_name,
                        properties={'attributes': []},
                        tags=[]
                    )
                    diagram.elements.append(element)
                continue
            
            # Relationship patterns: A ||--o{ B
            rel_patterns = [
                (r'(\w+)\s*\|\|--o\{\s*(\w+)', 'one_to_many'),
                (r'(\w+)\s*\}o--\|\|\s*(\w+)', 'many_to_one'),
                (r'(\w+)\s*\|\|--\|\|\s*(\w+)', 'one_to_one'),
                (r'(\w+)\s*\}o--o\{\s*(\w+)', 'many_to_many'),
            ]
            
            for pattern, rel_type in rel_patterns:
                match = re.match(pattern, line)
                if match:
                    source = match.group(1)
                    target = match.group(2)
                    
                    relationship = DiagramRelationship(
                        id=f"rel_{len(diagram.relationships) + 1}",
                        source_id=source,
                        target_id=target,
                        relationship_type=rel_type,
                        properties={},
                        tags=[]
                    )
                    diagram.relationships.append(relationship)
                    break
    
    def _parse_generic(self, content: str, diagram: ParsedDiagram):
        """Generic parsing for unknown diagram types."""
        # Extract any identifiable patterns
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for simple node definitions
            node_match = re.search(r'(\w+)', line)
            if node_match:
                node_id = node_match.group(1)
                
                # Check if this looks like an element definition
                if not any(elem.id == node_id for elem in diagram.elements):
                    element = DiagramElement(
                        id=node_id,
                        element_type=ElementType.COMPONENT,
                        name=node_id,
                        properties={},
                        tags=[]
                    )
                    diagram.elements.append(element)
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from Mermaid content."""
        metadata = {}
        
        # Extract title if present
        title_match = re.search(r'title\s+(.+)', content, re.IGNORECASE)
        if title_match:
            metadata['title'] = title_match.group(1).strip()
        
        return metadata
    
    def _extract_global_tags(self, content: str) -> List[str]:
        """Extract global tags from Mermaid content."""
        tags = []
        
        # Look for CSS class assignments or style definitions
        class_matches = re.findall(r'class\s+\w+\s+(\w+)', content)
        tags.extend(class_matches)
        
        return list(set(tags))  # Remove duplicates