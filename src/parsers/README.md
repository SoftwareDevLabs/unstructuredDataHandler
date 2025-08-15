# Parser Module Documentation

The parser module provides backend parsing capabilities for different diagram input formats (UML/SYSML). It extracts information from diagram sources and creates a relational database with relevant tags for downstream tool implementations.

## Supported Formats

### PlantUML (.puml, .plantuml, .pu)
- Class diagrams with attributes and methods
- Interface definitions
- Actors and components
- Inheritance, composition, aggregation, association, and dependency relationships
- Comments and metadata extraction

### Mermaid (.mmd, .mermaid)
- Class diagrams
- Flowcharts and graphs
- Sequence diagrams
- Entity-relationship diagrams
- Various node shapes and connection types

### DrawIO (.drawio, .xml)
- XML-based diagram formats
- Shape and connector extraction
- Style property parsing
- Position and geometry information

## Architecture

### Base Classes
- `BaseParser`: Abstract base class defining the parser interface
- `ParsedDiagram`: Container for parsed diagram data
- `DiagramElement`: Represents individual diagram elements
- `DiagramRelationship`: Represents relationships between elements

### Database Layer
- `DiagramDatabase`: SQLite-based storage for parsed diagrams
- Database models for diagrams, elements, and relationships
- Search and query capabilities
- Export functionality (JSON, CSV)

## Usage Example

```python
from parsers import PlantUMLParser, MermaidParser, DrawIOParser
from parsers.database import DiagramDatabase

# Initialize parser and database
parser = PlantUMLParser()
db = DiagramDatabase("diagrams.db")

# Parse diagram content
with open("diagram.puml", "r") as f:
    content = f.read()

parsed_diagram = parser.parse(content, "diagram.puml")

# Store in database
diagram_id = db.store_diagram(parsed_diagram)

# Query elements
elements = db.get_elements(diagram_id)
for element in elements:
    print(f"{element.element_type}: {element.name}")
```

## Testing

The module includes comprehensive unit tests for:
- Base parser functionality
- Format-specific parsing
- Database operations
- Search and export features

Run tests with: `python -m pytest test/unit/parsers/`

## Database Schema

### Diagrams Table
- `id`: Unique identifier
- `source_file`: Original file path
- `diagram_type`: Format type (plantuml, mermaid, drawio)
- `metadata`: JSON metadata
- `tags`: JSON tag array
- `created_at`, `updated_at`: Timestamps

### Elements Table
- `id`: Unique identifier
- `diagram_id`: Foreign key to diagrams
- `element_id`: Element identifier within diagram
- `element_type`: Type (class, interface, component, etc.)
- `name`: Element name
- `properties`: JSON properties
- `position`: JSON position data
- `tags`: JSON tag array

### Relationships Table
- `id`: Unique identifier
- `diagram_id`: Foreign key to diagrams
- `relationship_id`: Relationship identifier
- `source_element_id`: Source element
- `target_element_id`: Target element
- `relationship_type`: Type (inheritance, composition, etc.)
- `properties`: JSON properties
- `tags`: JSON tag array

## Extensibility

The modular design allows for easy addition of new diagram formats:

1. Inherit from `BaseParser`
2. Implement required abstract methods
3. Add format-specific parsing logic
4. Register in the main module

## Error Handling

- `ParseError`: Raised when diagram parsing fails
- Graceful handling of malformed content
- Validation of diagram integrity
- Database transaction safety