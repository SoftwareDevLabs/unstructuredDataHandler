"""
Tests for DrawIO parser.
"""

import pytest
from src.parsers.drawio_parser import DrawIOParser
from src.parsers.base_parser import DiagramType, ElementType, ParseError


class TestDrawIOParser:
    """Test DrawIO parser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DrawIOParser()
    
    def test_supported_extensions(self):
        """Test supported file extensions."""
        extensions = self.parser.supported_extensions
        assert '.drawio' in extensions
        assert '.xml' in extensions
    
    def test_diagram_type(self):
        """Test diagram type property."""
        assert self.parser.diagram_type == DiagramType.DRAWIO
    
    def test_parse_simple_xml(self):
        """Test parsing simple XML structure."""
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <mxfile host="app.diagrams.net" modified="2023-01-01T00:00:00.000Z">
            <diagram>
                <mxGraphModel>
                    <root>
                        <mxCell id="0"/>
                        <mxCell id="1" parent="0"/>
                        <mxCell id="2" value="TestClass" style="rounded=0" vertex="1" parent="1">
                            <mxGeometry x="160" y="80" width="120" height="60" as="geometry"/>
                        </mxCell>
                    </root>
                </mxGraphModel>
            </diagram>
        </mxfile>"""
        
        result = self.parser.parse(content, "test.drawio")
        
        assert result.diagram_type == DiagramType.DRAWIO
        assert result.source_file == "test.drawio"
        assert "host" in result.metadata
        assert "modified" in result.metadata
    
    def test_parse_style_properties(self):
        """Test parsing style properties."""
        style = "rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf"
        
        properties = self.parser._parse_style(style)
        
        assert properties["rounded"] == "0"
        assert properties["whiteSpace"] == "wrap"
        assert properties["html"] == "1"
        assert properties["fillColor"] == "#dae8fc"
        assert properties["strokeColor"] == "#6c8ebf"
    
    def test_determine_element_type(self):
        """Test element type determination."""
        # Test actor
        actor_style = "shape=umlActor;verticalLabelPosition=bottom"
        assert self.parser._determine_element_type(actor_style, "") == ElementType.ACTOR
        
        # Test interface
        interface_style = "ellipse;whiteSpace=wrap"
        assert self.parser._determine_element_type(interface_style, "I:TestInterface") == ElementType.INTERFACE
        
        # Test class
        class_style = "rounded=0;whiteSpace=wrap"
        assert self.parser._determine_element_type(class_style, "TestClass") == ElementType.CLASS
        
        # Test note
        note_style = "shape=note;whiteSpace=wrap"
        assert self.parser._determine_element_type(note_style, "") == ElementType.NOTE
    
    def test_determine_relationship_type(self):
        """Test relationship type determination."""
        # Test inheritance
        inheritance_style = "endArrow=block;endFill=0"
        assert self.parser._determine_relationship_type(inheritance_style, "extends") == "inheritance"
        
        # Test composition
        composition_style = "endArrow=diamond;endFill=1"
        assert self.parser._determine_relationship_type(composition_style, "") == "composition"
        
        # Test dependency
        dependency_style = "dashed=1;endArrow=open"
        assert self.parser._determine_relationship_type(dependency_style, "") == "dependency"
        
        # Test association (default)
        association_style = "endArrow=none"
        assert self.parser._determine_relationship_type(association_style, "") == "association"
    
    def test_extract_text_content(self):
        """Test text content extraction."""
        # Test simple text
        simple_text = "TestClass"
        assert self.parser._extract_text_content(simple_text) == "TestClass"
        
        # Test HTML content
        html_text = "&lt;b&gt;TestClass&lt;/b&gt;"
        assert self.parser._extract_text_content(html_text) == "<b>TestClass</b>"
        
        # Test with HTML tags
        tagged_text = "<p>TestClass</p>"
        assert self.parser._extract_text_content(tagged_text) == "TestClass"
    
    def test_extract_element_tags(self):
        """Test element tag extraction."""
        style = "shape=rectangle;fillColor=#dae8fc;strokeColor=#6c8ebf"
        value = "class TestClass"
        
        tags = self.parser._extract_element_tags(style, value)
        
        # Should extract style-based tags
        assert any("shape:rectangle" in tag for tag in tags)
        assert any("fillColor:#dae8fc" in tag for tag in tags)
        
        # Should extract content-based tags
        assert "class" in tags
    
    def test_parse_direct_xml_elements(self):
        """Test parsing XML elements directly."""
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <mxGraphModel>
            <root>
                <mxCell id="0"/>
                <mxCell id="1" parent="0"/>
                <mxCell id="class1" value="TestClass" style="rounded=0;whiteSpace=wrap;html=1" vertex="1" parent="1">
                    <mxGeometry x="160" y="80" width="120" height="60" as="geometry"/>
                </mxCell>
                <mxCell id="class2" value="AnotherClass" style="rounded=0;whiteSpace=wrap;html=1" vertex="1" parent="1">
                    <mxGeometry x="320" y="80" width="120" height="60" as="geometry"/>
                </mxCell>
                <mxCell id="rel1" value="" style="endArrow=classic;html=1" edge="1" parent="1" source="class1" target="class2">
                    <mxGeometry width="50" height="50" relative="1" as="geometry"/>
                </mxCell>
            </root>
        </mxGraphModel>"""
        
        result = self.parser.parse(content)
        
        # Should parse elements
        assert len(result.elements) == 2
        
        # Check element properties
        test_class = next((e for e in result.elements if e.name == "TestClass"), None)
        assert test_class is not None
        assert test_class.id == "class1"
        assert test_class.position is not None
        assert test_class.position["x"] == 160.0
        assert test_class.position["y"] == 80.0
        
        # Should parse relationships
        assert len(result.relationships) == 1
        relationship = result.relationships[0]
        assert relationship.source_id == "class1"
        assert relationship.target_id == "class2"
    
    def test_parse_empty_content(self):
        """Test parsing empty or minimal content."""
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <mxfile>
            <diagram>
            </diagram>
        </mxfile>"""
        
        result = self.parser.parse(content)
        
        assert result.diagram_type == DiagramType.DRAWIO
        assert len(result.elements) == 0
        assert len(result.relationships) == 0
    
    def test_parse_invalid_xml(self):
        """Test error handling for invalid XML."""
        invalid_content = "This is not valid XML content"
        
        with pytest.raises(ParseError) as exc_info:
            self.parser.parse(invalid_content)
        
        assert "Invalid XML format" in str(exc_info.value)
    
    def test_parse_with_geometry(self):
        """Test parsing elements with geometry information."""
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <mxGraphModel>
            <root>
                <mxCell id="0"/>
                <mxCell id="1" parent="0"/>
                <mxCell id="rect1" value="Rectangle" style="rounded=0" vertex="1" parent="1">
                    <mxGeometry x="100" y="200" width="150" height="80" as="geometry"/>
                </mxCell>
            </root>
        </mxGraphModel>"""
        
        result = self.parser.parse(content)
        
        assert len(result.elements) == 1
        element = result.elements[0]
        
        # Check position
        assert element.position is not None
        assert element.position["x"] == 100.0
        assert element.position["y"] == 200.0
        
        # Check size in properties
        assert "size" in element.properties
        assert element.properties["size"]["width"] == 150.0
        assert element.properties["size"]["height"] == 80.0
    
    def test_decode_diagram_data(self):
        """Test decoding compressed diagram data."""
        # Test with empty data
        assert self.parser._decode_diagram_data("") is None
        assert self.parser._decode_diagram_data(None) is None
        
        # Test with invalid data (should not crash)
        invalid_data = "invalid_base64_data"
        result = self.parser._decode_diagram_data(invalid_data)
        # Should return None or handle gracefully
        assert result is None or isinstance(result, str)
    
    def test_parse_connector_properties(self):
        """Test parsing connector properties."""
        content = """<?xml version="1.0" encoding="UTF-8"?>
        <mxGraphModel>
            <root>
                <mxCell id="0"/>
                <mxCell id="1" parent="0"/>
                <mxCell id="src" value="Source" style="rounded=0" vertex="1" parent="1">
                    <mxGeometry x="100" y="100" width="100" height="50" as="geometry"/>
                </mxCell>
                <mxCell id="tgt" value="Target" style="rounded=0" vertex="1" parent="1">
                    <mxGeometry x="300" y="100" width="100" height="50" as="geometry"/>
                </mxCell>
                <mxCell id="conn" value="connects" style="endArrow=classic;html=1;dashed=1" edge="1" parent="1" source="src" target="tgt">
                    <mxGeometry width="50" height="50" relative="1" as="geometry"/>
                </mxCell>
            </root>
        </mxGraphModel>"""
        
        result = self.parser.parse(content)
        
        # Should have elements and relationship
        assert len(result.elements) == 2
        assert len(result.relationships) == 1
        
        relationship = result.relationships[0]
        assert relationship.source_id == "src"
        assert relationship.target_id == "tgt"
        assert relationship.properties.get("label") == "connects"
        
        # Should detect dashed style as dependency
        assert relationship.relationship_type == "dependency"