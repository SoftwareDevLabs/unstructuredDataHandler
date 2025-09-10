"""
DrawIO parser for extracting diagram information.

This parser handles DrawIO format files (.drawio, .xml) and extracts
shapes, connectors, and other diagram elements from the XML structure.
"""

import xml.etree.ElementTree as ET
import json
import base64
import zlib
import urllib.parse
from typing import List, Dict, Any, Optional
from .base_parser import BaseParser, ParsedDiagram, DiagramElement, DiagramRelationship
from .base_parser import DiagramType, ElementType, ParseError


class DrawIOParser(BaseParser):
    """Parser for DrawIO diagram files."""
    
    @property
    def supported_extensions(self) -> List[str]:
        return ['.drawio', '.xml']
    
    @property
    def diagram_type(self) -> DiagramType:
        return DiagramType.DRAWIO
    
    def parse(self, content: str, source_file: str = "") -> ParsedDiagram:
        """Parse DrawIO content and extract diagram information."""
        try:
            diagram = ParsedDiagram(
                diagram_type=self.diagram_type,
                source_file=source_file
            )
            
            # Parse XML content
            root = ET.fromstring(content)
            
            # Extract metadata
            diagram.metadata = self._extract_metadata(root)
            
            # Find diagram pages
            diagrams = root.findall('.//diagram')
            
            if diagrams:
                # Process first diagram page (multi-page support can be added later)
                diagram_data = self._decode_diagram_data(diagrams[0].text)
                if diagram_data:
                    self._parse_diagram_data(diagram_data, diagram)
            else:
                # Direct XML format (not compressed)
                self._parse_direct_xml(root, diagram)
            
            return diagram
            
        except ET.ParseError as e:
            raise ParseError(f"Invalid XML format: {str(e)}")
        except Exception as e:
            raise ParseError(f"Failed to parse DrawIO content: {str(e)}")
    
    def _extract_metadata(self, root: ET.Element) -> Dict[str, Any]:
        """Extract metadata from the root element."""
        metadata = {}
        
        # Extract file properties
        if root.tag == 'mxfile':
            metadata['host'] = root.get('host', '')
            metadata['modified'] = root.get('modified', '')
            metadata['agent'] = root.get('agent', '')
            metadata['version'] = root.get('version', '')
        
        return metadata
    
    def _decode_diagram_data(self, encoded_data: str) -> Optional[str]:
        """Decode compressed diagram data."""
        if not encoded_data:
            return None
        
        try:
            # DrawIO uses URL-encoded, base64-encoded, deflate-compressed XML
            url_decoded = urllib.parse.unquote(encoded_data)
            base64_decoded = base64.b64decode(url_decoded)
            decompressed = zlib.decompress(base64_decoded, -zlib.MAX_WBITS)
            return decompressed.decode('utf-8')
        except Exception:
            # Try direct base64 decoding
            try:
                base64_decoded = base64.b64decode(encoded_data)
                return base64_decoded.decode('utf-8')
            except Exception:
                return None
    
    def _parse_diagram_data(self, diagram_xml: str, diagram: ParsedDiagram):
        """Parse the decoded diagram XML data."""
        try:
            root = ET.fromstring(diagram_xml)
            self._parse_direct_xml(root, diagram)
        except ET.ParseError:
            # If parsing fails, treat as invalid data
            pass
    
    def _parse_direct_xml(self, root: ET.Element, diagram: ParsedDiagram):
        """Parse XML elements directly."""
        # Find all cells (shapes and connectors)
        cells = root.findall('.//mxCell')
        
        # Separate elements and relationships
        elements_map = {}
        
        for cell in cells:
            cell_id = cell.get('id', '')
            if not cell_id or cell_id in ['0', '1']:  # Skip root cells
                continue
            
            # Check if this is a connector (edge)
            if cell.get('edge') == '1':
                self._parse_connector(cell, diagram)
            else:
                # Parse as element (vertex)
                element = self._parse_element(cell)
                if element:
                    diagram.elements.append(element)
                    elements_map[cell_id] = element
    
    def _parse_element(self, cell: ET.Element) -> Optional[DiagramElement]:
        """Parse a cell as a diagram element."""
        cell_id = cell.get('id', '')
        value = cell.get('value', '')
        style = cell.get('style', '')
        
        # Determine element type based on style
        element_type = self._determine_element_type(style, value)
        
        # Extract position and size
        geometry = cell.find('mxGeometry')
        position = None
        size = None
        
        if geometry is not None:
            x = geometry.get('x')
            y = geometry.get('y')
            width = geometry.get('width')
            height = geometry.get('height')
            
            if x is not None and y is not None:
                position = {'x': float(x), 'y': float(y)}
            
            if width is not None and height is not None:
                size = {'width': float(width), 'height': float(height)}
        
        # Parse style properties
        style_props = self._parse_style(style)
        
        properties = {
            'style': style_props,
            'original_style': style
        }
        
        if size:
            properties['size'] = size
        
        # Extract text content
        name = self._extract_text_content(value)
        
        element = DiagramElement(
            id=cell_id,
            element_type=element_type,
            name=name,
            properties=properties,
            position=position,
            tags=self._extract_element_tags(style, value)
        )
        
        return element
    
    def _parse_connector(self, cell: ET.Element, diagram: ParsedDiagram):
        """Parse a connector (edge) as a relationship."""
        cell_id = cell.get('id', '')
        source = cell.get('source', '')
        target = cell.get('target', '')
        value = cell.get('value', '')
        style = cell.get('style', '')
        
        if not source or not target:
            return
        
        # Determine relationship type from style
        rel_type = self._determine_relationship_type(style, value)
        
        # Parse style properties
        style_props = self._parse_style(style)
        
        properties = {
            'style': style_props,
            'original_style': style
        }
        
        # Extract label text
        if value:
            properties['label'] = self._extract_text_content(value)
        
        relationship = DiagramRelationship(
            id=cell_id,
            source_id=source,
            target_id=target,
            relationship_type=rel_type,
            properties=properties,
            tags=self._extract_element_tags(style, value)
        )
        
        diagram.relationships.append(relationship)
    
    def _determine_element_type(self, style: str, value: str) -> ElementType:
        """Determine element type based on style and content."""
        style_lower = style.lower()
        value_lower = value.lower() if value else ''
        
        # Check for specific shapes
        if 'umlactor' in style_lower or 'actor' in value_lower:
            return ElementType.ACTOR
        elif 'rhombus' in style_lower or 'diamond' in style_lower:
            return ElementType.BOUNDARY
        elif 'cylinder' in style_lower or 'database' in style_lower:
            return ElementType.ENTITY
        elif 'ellipse' in style_lower and ('interface' in value_lower or 'i:' in value_lower):
            return ElementType.INTERFACE
        elif 'rectangle' in style_lower or 'class' in value_lower:
            return ElementType.CLASS
        elif 'note' in style_lower:
            return ElementType.NOTE
        else:
            return ElementType.COMPONENT
    
    def _determine_relationship_type(self, style: str, value: str) -> str:
        """Determine relationship type based on style and content."""
        style_props = self._parse_style(style)
        value_lower = value.lower() if value else ""

        end_arrow = style_props.get("endArrow")
        end_fill = style_props.get("endFill")

        if end_arrow == "block" and end_fill == "0":
            return "inheritance"
        if end_arrow == "diamond" and end_fill == "1":
            return "composition"
        if end_arrow == "diamond" and end_fill == "0":
            return "aggregation"
        if style_props.get("dashed") == "1":
            return "dependency"
        if "extends" in value_lower:
            return "inheritance"
        if "implements" in value_lower:
            return "realization"
        
        return "association"
    
    def _parse_style(self, style: str) -> Dict[str, str]:
        """Parse DrawIO style string into properties."""
        properties = {}
        
        if not style:
            return properties
        
        # Split style by semicolons
        style_parts = style.split(';')
        
        for part in style_parts:
            if '=' in part:
                key, value = part.split('=', 1)
                properties[key] = value
            else:
                # Style without value (like shape names)
                properties[part] = 'true'
        
        return properties
    
    def _extract_text_content(self, value: str) -> str:
        """Extract text content from HTML-like value."""
        if not value:
            return ''
        
        # Remove HTML tags if present
        import re
        clean_text = re.sub(r'<[^>]+>', '', value)
        
        # Decode HTML entities
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&quot;', '"')
        
        return clean_text.strip()
    
    def _extract_element_tags(self, style: str, value: str) -> List[str]:
        """Extract tags from style and value."""
        tags = []
        
        # Extract style-based tags
        style_props = self._parse_style(style)
        
        # Add significant style properties as tags
        significant_props = ['shape', 'fillColor', 'strokeColor', 'fontFamily']
        for prop in significant_props:
            if prop in style_props:
                tags.append(f"{prop}:{style_props[prop]}")
        
        # Extract content-based tags
        if value:
            value_lower = value.lower()
            if 'class' in value_lower:
                tags.append('class')
            if 'interface' in value_lower:
                tags.append('interface')
            if 'abstract' in value_lower:
                tags.append('abstract')
        
        return tags