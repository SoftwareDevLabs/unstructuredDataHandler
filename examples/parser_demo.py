#!/usr/bin/env python3
"""
Example script demonstrating the parser functionality.

This script shows how to use the different parsers to extract information
from diagram files and store them in the database.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from parsers import PlantUMLParser, MermaidParser, DrawIOParser
from parsers.database import DiagramDatabase, get_diagram_statistics
from parsers.base_parser import DiagramType


def create_sample_diagrams():
    """Create sample diagram content for testing."""
    
    plantuml_content = """
    @startuml
    title Sample Class Diagram
    
    class User {
        +id: String
        +name: String
        +email: String
        +login(): boolean
        +logout(): void
    }
    
    class Admin {
        +permissions: List<String>
        +manageUsers(): void
    }
    
    interface Authenticatable {
        +authenticate(): boolean
    }
    
    User <|-- Admin
    User ..|> Authenticatable
    @enduml
    """
    
    mermaid_content = """
    classDiagram
    class Animal {
        +String name
        +int age
        +makeSound() void
    }
    class Dog {
        +String breed
        +bark() void
    }
    class Cat {
        +int lives
        +meow() void
    }
    Animal <|-- Dog
    Animal <|-- Cat
    """
    
    drawio_content = """<?xml version="1.0" encoding="UTF-8"?>
    <mxGraphModel>
        <root>
            <mxCell id="0"/>
            <mxCell id="1" parent="0"/>
            <mxCell id="user" value="User" style="rounded=0;whiteSpace=wrap;html=1" vertex="1" parent="1">
                <mxGeometry x="160" y="80" width="120" height="60" as="geometry"/>
            </mxCell>
            <mxCell id="system" value="System" style="rounded=0;whiteSpace=wrap;html=1" vertex="1" parent="1">
                <mxGeometry x="320" y="80" width="120" height="60" as="geometry"/>
            </mxCell>
            <mxCell id="conn1" value="uses" style="endArrow=classic;html=1" edge="1" parent="1" source="user" target="system">
                <mxGeometry width="50" height="50" relative="1" as="geometry"/>
            </mxCell>
        </root>
    </mxGraphModel>"""
    
    return {
        'plantuml': plantuml_content,
        'mermaid': mermaid_content,
        'drawio': drawio_content
    }


def main():
    """Main demonstration function."""
    print("🔍 Diagram Parser Demo")
    print("=" * 50)
    
    # Initialize database
    db = DiagramDatabase("demo_diagrams.db")
    print("✅ Database initialized")
    
    # Create parsers
    parsers = {
        'PlantUML': PlantUMLParser(),
        'Mermaid': MermaidParser(),
        'DrawIO': DrawIOParser()
    }
    
    # Get sample diagrams
    samples = create_sample_diagrams()
    
    diagram_ids = []
    
    # Parse and store each diagram type
    for parser_name, parser in parsers.items():
        print(f"\n📊 Testing {parser_name} Parser")
        print("-" * 30)
        
        if parser_name == 'PlantUML':
            content = samples['plantuml']
            filename = "sample.puml"
        elif parser_name == 'Mermaid':
            content = samples['mermaid']
            filename = "sample.mmd"
        else:  # DrawIO
            content = samples['drawio']
            filename = "sample.drawio"
        
        try:
            # Parse the content
            parsed = parser.parse(content, filename)
            
            print(f"  📄 Source: {parsed.source_file}")
            print(f"  🔢 Elements: {len(parsed.elements)}")
            print(f"  🔗 Relationships: {len(parsed.relationships)}")
            print(f"  🏷️  Tags: {len(parsed.tags)}")
            
            # Store in database
            diagram_id = db.store_diagram(parsed)
            diagram_ids.append(diagram_id)
            print(f"  💾 Stored with ID: {diagram_id}")
            
            # Show element details
            for element in parsed.elements[:3]:  # Show first 3 elements
                print(f"    - {element.element_type.value}: {element.name}")
            
            if len(parsed.elements) > 3:
                print(f"    ... and {len(parsed.elements) - 3} more")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Show database statistics
    print(f"\n📈 Database Statistics")
    print("-" * 30)
    
    all_diagrams = db.get_all_diagrams()
    print(f"  📊 Total diagrams: {len(all_diagrams)}")
    
    for diagram_id in diagram_ids:
        stats = get_diagram_statistics(db, diagram_id)
        diagram = db.get_diagram(diagram_id)
        if diagram:
            print(f"  \n🔍 {diagram.source_file} ({diagram.diagram_type}):")
            print(f"    - Elements: {stats['total_elements']}")
            print(f"    - Relationships: {stats['total_relationships']}")
            print(f"    - Element types: {list(stats['element_type_counts'].keys())}")
    
    # Demonstrate search functionality
    print(f"\n🔍 Search Examples")
    print("-" * 30)
    
    # Search by element type
    classes = db.search_elements_by_type("class")
    print(f"  📋 Found {len(classes)} class elements")
    
    # Search by tags (if any were created)
    tag_results = db.search_by_tags(["important", "core", "api"])
    total_tagged = sum(len(results) for results in tag_results.values())
    print(f"  🏷️  Found {total_tagged} tagged items")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"💾 Database saved as: demo_diagrams.db")


if __name__ == "__main__":
    main()