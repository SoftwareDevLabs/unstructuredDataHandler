"""
Authentication and authorization decorators.
"""
from functools import wraps
from flask import flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required as flask_login_required


def login_required(f):
    """Decorator to require user authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('You need to be logged in to access this page.', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def require_role(role_name):
    """Decorator to require specific role for access."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('You need to be logged in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_role(role_name):
                if request.is_json:
                    return jsonify({'error': f'Role "{role_name}" required'}), 403
                flash(f'You need "{role_name}" role to access this page.', 'error')
                return redirect(url_for('auth.unauthorized'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_any_role(*role_names):
    """Decorator to require any of the specified roles for access."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('You need to be logged in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            has_required_role = any(current_user.has_role(role) for role in role_names)
            if not has_required_role:
                if request.is_json:
                    return jsonify({'error': f'One of roles {role_names} required'}), 403
                flash(f'You need one of these roles to access this page: {", ".join(role_names)}', 'error')
                return redirect(url_for('auth.unauthorized'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator to require admin role."""
    return require_role('admin')(f)


def api_key_required(f):
    """Decorator to require API key authentication for API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Here you would validate the API key against your database
        # For now, we'll use a simple check (replace with proper validation)
        if api_key != 'your-api-key-here':  # Replace with proper validation
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function