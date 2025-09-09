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
        created_nodes = set()

        def parse_and_create_node(node_str: str):
            """Parse a node string and create a DiagramElement if it doesn't exist."""
            node_str = node_str.strip()
            node_patterns = [
                (r'^(\w+)\s*\(\((.*)\)\)$', 'circle'),
                (r'^(\w+)\s*\[(.*)\]$', 'rectangular'),
                (r'^(\w+)\s*\((.*)\)$', 'rounded'),
                (r'^(\w+)\s*\{(.*)\}$', 'diamond'),
            ]
            for pattern, shape in node_patterns:
                match = re.match(pattern, node_str)
                if match:
                    node_id, label = match.groups()
                    if node_id not in created_nodes:
                        element = DiagramElement(
                            id=node_id, element_type=ElementType.COMPONENT,
                            name=label, properties={'shape': shape}, tags=[]
                        )
                        diagram.elements.append(element)
                        created_nodes.add(node_id)
                    return node_id
            
            node_id = node_str
            if node_id and node_id not in created_nodes:
                element = DiagramElement(
                    id=node_id, element_type=ElementType.COMPONENT,
                    name=node_id, properties={'shape': 'simple'}, tags=[]
                )
                diagram.elements.append(element)
                created_nodes.add(node_id)
            return node_id

        for line in lines:
            line = line.strip()
            if not line:
                continue

            connection_patterns = [
                (r'-->', 'directed'), (r'---', 'undirected'),
                (r'-.->', 'dotted'), (r'==>', 'thick')
            ]
            
            found_connection = False
            for arrow, style in connection_patterns:
                if arrow in line:
                    parts = line.split(arrow, 1)
                    source_str = parts[0]
                    target_and_label_str = parts[1]

                    label_match = re.match(r'\s*\|(.*?)\|(.*)', target_and_label_str)
                    if label_match:
                        label = label_match.group(1)
                        target_str = label_match.group(2).strip()
                    else:
                        label = None
                        target_str = target_and_label_str.strip()
                    
                    source_id = parse_and_create_node(source_str)
                    target_id = parse_and_create_node(target_str)
                    
                    if source_id and target_id:
                        properties = {'style': style}
                        if label:
                            properties['label'] = label

                        relationship = DiagramRelationship(
                            id=f"rel_{len(diagram.relationships) + 1}",
                            source_id=source_id, target_id=target_id,
                            relationship_type='connection', properties=properties, tags=[]
                        )
                        diagram.relationships.append(relationship)
                        found_connection = True
                        break

            if not found_connection:
                parse_and_create_node(line)
    
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
                (r'(\w+)\s*-->>\s*(\w+)\s*:\s*(.+)', 'return_message'),
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
        # Parse entities first, handling multiline blocks
        entity_pattern = r'(\w+)\s*\{([^}]*)\}'
        entities_found = re.findall(entity_pattern, content, re.DOTALL)
        
        for entity_name, attributes_text in entities_found:
            attributes = []
            if attributes_text:
                attr_lines = [attr.strip() for attr in attributes_text.split('\n') if attr.strip()]
                for attr_line in attr_lines:
                    if attr_line:
                        attributes.append(attr_line)

            element = DiagramElement(
                id=entity_name,
                element_type=ElementType.ENTITY,
                name=entity_name,
                properties={'attributes': attributes},
                tags=[]
            )
            diagram.elements.append(element)

        # Remove entity blocks from content to parse relationships
        content_after_entities = re.sub(entity_pattern, '', content, flags=re.DOTALL)
        lines = content_after_entities.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Relationship patterns
            rel_patterns = [
                (r'(\w+)\s*\|\|--o\{\s*(\w+)', 'one_to_many'),
                (r'(\w+)\s*\}o--\|\|\s*(\w+)', 'many_to_one'),
                (r'(\w+)\s*\|\|--\|\|\s*(\w+)', 'one_to_one'),
                (r'(\w+)\s*\}o--o\{\s*(\w+)', 'many_to_many'),
            ]
            
            for pattern, rel_type in rel_patterns:
                match = re.search(pattern, line)
                if match:
                    source, target = match.groups()
                    
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