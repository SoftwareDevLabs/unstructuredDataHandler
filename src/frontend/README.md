# Frontend Infrastructure for Role & Authentication

This module provides a comprehensive frontend infrastructure with role-based authentication for the SDLC Core system.

## Features

### 🔐 Authentication System
- **User Registration & Login**: Secure user account creation and authentication
- **Password Security**: Bcrypt password hashing for security
- **Session Management**: Flask-Login for session handling
- **CSRF Protection**: Built-in CSRF protection for forms

### 👥 Role-Based Access Control (RBAC)
- **Flexible Role System**: Support for multiple user roles
- **Role Decorators**: Easy-to-use decorators for protecting routes
- **Default Roles**: Pre-configured roles (admin, user, moderator, analyst, developer)
- **Dynamic Permissions**: Runtime role checking and permission enforcement

### 🌐 Web Interface
- **Responsive Design**: Bootstrap 5 responsive web interface
- **Modern UI**: Clean, professional interface with icons and animations
- **Dashboard**: User dashboard with profile information
- **Admin Panel**: Comprehensive admin interface for user/role management

### 🔌 API Endpoints
- **RESTful API**: JSON API endpoints for authentication
- **User Profile API**: Programmatic access to user information
- **Admin API**: Administrative endpoints for user management
- **Error Handling**: Consistent error responses with proper HTTP status codes

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
cd src/frontend
python app.py
```

### 3. Access the Application
- **Home**: http://localhost:5000/
- **Login**: http://localhost:5000/auth/login
- **Register**: http://localhost:5000/auth/register
- **Admin Panel**: http://localhost:5000/admin (admin role required)

### 4. Default Admin Account
- **Username**: admin
- **Password**: admin123
- ⚠️ **Important**: Change the admin password after first login!

## Architecture

### Models
- **User**: Core user model with authentication capabilities
- **Role**: Role definition with description
- **UserRole**: Many-to-many relationship between users and roles

### Views
- **Authentication Routes**: Login, register, logout, unauthorized
- **Main Routes**: Index, dashboard, admin panel
- **API Routes**: JSON endpoints for programmatic access

### Security Features
- **Password Hashing**: Secure bcrypt password storage
- **Session Security**: Secure session management with Flask-Login
- **CSRF Protection**: Built-in CSRF token validation
- **Role Validation**: Server-side role validation for all protected routes

## API Reference

### Authentication Endpoints

#### POST /auth/api/login
Login a user and return user information.

**Request:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "string",
        "email": "string",
        "roles": ["role1", "role2"]
    }
}
```

#### GET /auth/api/user/profile
Get current user profile (requires authentication).

**Response:**
```json
{
    "user": {
        "id": 1,
        "username": "string",
        "email": "string",
        "roles": ["role1", "role2"],
        "is_active": true,
        "created_at": "2024-01-01T00:00:00",
        "last_login": "2024-01-01T00:00:00"
    }
}
```

### Admin Endpoints

#### GET /api/admin/users
Get all users (admin only).

#### GET /api/admin/roles
Get all roles (admin only).

## Role System

### Default Roles
- **admin**: Full system administrator access
- **user**: Standard user access
- **moderator**: Content moderation access
- **analyst**: Data analysis and reporting access
- **developer**: Development and API access

### Using Role Decorators

```python
from frontend.decorators import require_role, admin_required, login_required

@require_role('admin')
def admin_only_view():
    return "Admin content"

@admin_required
def another_admin_view():
    return "Also admin content"

@login_required
def authenticated_view():
    return "Requires login"
```

### Checking Roles in Templates
```html
{% if current_user.has_role('admin') %}
    <a href="/admin">Admin Panel</a>
{% endif %}
```

## Configuration

### Environment Variables
- **SECRET_KEY**: Flask secret key for sessions (required in production)
- **DATABASE_URL**: Database connection string (default: SQLite)
- **FLASK_ENV**: Environment setting (development/production)
- **PORT**: Port to run on (default: 5000)

### Database
The system uses SQLAlchemy with support for multiple database backends:
- **SQLite**: Default, good for development
- **PostgreSQL**: Recommended for production
- **MySQL**: Also supported

## Testing

Run the test suite:
```bash
pytest test/unit/frontend/
```

Tests cover:
- User model functionality
- Role system
- Authentication flows
- API endpoints
- Access control

## Security Considerations

### Production Deployment
1. **Change Default Credentials**: Update admin password immediately
2. **Set SECRET_KEY**: Use a secure, random secret key
3. **Use HTTPS**: Always use HTTPS in production
4. **Database Security**: Use a production database with proper credentials
5. **Environment Variables**: Store sensitive config in environment variables

### Best Practices
- Regular password updates
- Monitor failed login attempts
- Audit user roles and permissions
- Keep dependencies updated
- Use secure session settings

## File Structure

```
src/frontend/
├── __init__.py          # Module initialization
├── app.py              # Application entry point
├── auth.py             # Authentication routes and app factory
├── models.py           # Database models
├── forms.py            # WTForms form definitions
├── decorators.py       # Authentication decorators
├── static/
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── app.js      # Frontend JavaScript
└── templates/
    ├── base.html       # Base template
    ├── index.html      # Home page
    ├── dashboard.html  # User dashboard
    ├── admin.html      # Admin panel
    └── auth/
        ├── login.html      # Login form
        ├── register.html   # Registration form
        └── unauthorized.html # Access denied page
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation for changes
4. Ensure security best practices

## License

This project is part of the SDLC Core system. See the main project license for details.