# Frontend Infrastructure Integration Guide

## Overview

The frontend infrastructure has been successfully implemented and integrated into the SDLC Core system. This guide explains how to use and integrate the authentication system with the existing components.

## Quick Start

### 1. Starting the Frontend
```bash
cd src/frontend
python app.py
```

### 2. Default Access
- **URL**: http://localhost:5000
- **Admin Username**: admin
- **Admin Password**: admin123

## Integration with Existing Components

### Using Authentication in Your Code

```python
# Import the frontend components
from src.frontend import create_app, User, Role, require_role, login_required

# Example: Protecting an API endpoint
from src.frontend.decorators import require_role

@require_role('developer')
def my_protected_api():
    return {"message": "Developer access granted"}

# Example: Checking user roles
from flask_login import current_user

if current_user.has_role('admin'):
    # Admin functionality
    pass
```

### Database Integration

The frontend uses SQLAlchemy models that can be extended:

```python
from src.frontend.models import db, User

# Add custom fields to user
class ExtendedUser(User):
    __tablename__ = 'users'
    
    # Add custom fields
    department = db.Column(db.String(100))
    preferences = db.Column(db.JSON)
```

### API Integration

The system provides REST API endpoints that can be used by other components:

```python
import requests

# Login via API
response = requests.post('http://localhost:5000/auth/api/login', 
    json={'username': 'admin', 'password': 'admin123'})

# Get user profile
response = requests.get('http://localhost:5000/auth/api/user/profile')
```

## Role-Based Access Control

### Available Roles
- **admin**: Full system access
- **user**: Standard user access  
- **moderator**: Content moderation
- **analyst**: Data analysis and reporting
- **developer**: Development and API access

### Using Roles in Components

```python
# In LLM components
from src.frontend.decorators import require_role

@require_role('analyst')
def generate_analytics_report():
    # Only analysts can generate reports
    pass

# In agents
@require_role('developer')
def deploy_agent():
    # Only developers can deploy agents
    pass
```

## Configuration

### Environment Variables
```bash
export SECRET_KEY="your-production-secret-key"
export DATABASE_URL="postgresql://user:pass@localhost/sdlc_core"
export WTF_CSRF_ENABLED="true"
```

### Production Deployment
1. Set secure SECRET_KEY
2. Use PostgreSQL database
3. Enable HTTPS
4. Change default admin password
5. Configure proper CORS settings

## Security Considerations

1. **Password Security**: Uses bcrypt hashing
2. **Session Security**: Flask-Login session management
3. **CSRF Protection**: Built-in CSRF token validation
4. **Role Validation**: Server-side role checking
5. **API Security**: JWT tokens can be added for API authentication

## Extending the System

### Adding New Roles
```python
# Add in models.py or via admin interface
new_role = Role(name='researcher', description='Research access')
db.session.add(new_role)
db.session.commit()
```

### Custom Decorators
```python
from src.frontend.decorators import require_any_role

@require_any_role('admin', 'developer', 'analyst')
def advanced_feature():
    pass
```

### Adding Custom Routes
```python
from src.frontend.auth import main_bp
from src.frontend.decorators import login_required

@main_bp.route('/custom-feature')
@login_required
def custom_feature():
    return render_template('custom.html')
```

## Testing

Run the authentication tests:
```bash
PYTHONPATH=src python -m pytest test/unit/frontend/ -v
```

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure PYTHONPATH includes src directory
2. **Database Errors**: Check database permissions and connectivity
3. **CSRF Errors**: Disable CSRF for API testing with WTF_CSRF_ENABLED=false
4. **Role Errors**: Ensure users have appropriate roles assigned

### Debug Mode
```bash
FLASK_ENV=development python app.py
```

## Next Steps

1. Integrate with existing LLM components
2. Add API authentication tokens
3. Implement user preferences and profiles
4. Add audit logging for security events
5. Integrate with CI/CD pipelines for role-based deployments