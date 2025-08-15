# Frontend Infrastructure Module
from .auth import create_app, auth_bp, main_bp
from .models import db, User, Role, UserRole, init_default_roles
from .decorators import require_role, login_required, admin_required, require_any_role
from .forms import LoginForm, RegisterForm, ChangePasswordForm, UserEditForm, RoleAssignmentForm

__all__ = [
    'create_app', 'auth_bp', 'main_bp', 'db',
    'User', 'Role', 'UserRole', 'init_default_roles',
    'require_role', 'login_required', 'admin_required', 'require_any_role',
    'LoginForm', 'RegisterForm', 'ChangePasswordForm', 'UserEditForm', 'RoleAssignmentForm'
]

__version__ = '1.0.0'