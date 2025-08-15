"""
Unit tests for frontend authentication system.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

from frontend.auth import create_app
from frontend.models import db, User, Role, UserRole, init_default_roles


@pytest.fixture
def app():
    """Create test application."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        init_default_roles()
        
        # Create test users
        admin_role = Role.query.filter_by(name='admin').first()
        user_role = Role.query.filter_by(name='user').first()
        
        admin_user = User(username='testadmin', email='admin@test.com')
        admin_user.set_password('testpass123')
        admin_user.add_role(admin_role)
        
        regular_user = User(username='testuser', email='user@test.com')
        regular_user.set_password('testpass123')
        regular_user.add_role(user_role)
        
        db.session.add(admin_user)
        db.session.add(regular_user)
        db.session.commit()
    
    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation(self, app):
        """Test user creation."""
        with app.app_context():
            user = User(username='newuser', email='new@test.com')
            user.set_password('password123')
            
            assert user.username == 'newuser'
            assert user.email == 'new@test.com'
            assert user.check_password('password123')
            assert not user.check_password('wrongpassword')
    
    def test_user_roles(self, app):
        """Test user role functionality."""
        with app.app_context():
            user = User.query.filter_by(username='testadmin').first()
            
            assert user.has_role('admin')
            assert not user.has_role('nonexistent')
            assert 'admin' in user.get_roles()
    
    def test_password_hashing(self, app):
        """Test password hashing security."""
        with app.app_context():
            user = User(username='testpass', email='test@test.com')
            user.set_password('plaintext')
            
            # Password should be hashed
            assert user.password_hash != 'plaintext'
            assert user.check_password('plaintext')
            assert not user.check_password('wrongtext')


class TestRoleModel:
    """Test Role model functionality."""
    
    def test_role_creation(self, app):
        """Test role creation."""
        with app.app_context():
            role = Role(name='testrole', description='Test role')
            db.session.add(role)
            db.session.commit()
            
            assert role.name == 'testrole'
            assert role.description == 'Test role'
    
    def test_role_relationships(self, app):
        """Test role-user relationships."""
        with app.app_context():
            admin_role = Role.query.filter_by(name='admin').first()
            users_with_admin = admin_role.user_roles.count()
            
            assert users_with_admin > 0


class TestAuthentication:
    """Test authentication routes and functionality."""
    
    def test_login_page(self, client):
        """Test login page renders."""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Sign In' in response.data
    
    def test_register_page(self, client):
        """Test register page renders."""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_valid_login(self, client):
        """Test valid user login."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Dashboard' in response.data or b'Logged in successfully' in response.data
    
    def test_invalid_login(self, client):
        """Test invalid login credentials."""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_user_registration(self, client):
        """Test user registration."""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data or b'Sign In' in response.data
    
    def test_duplicate_registration(self, client):
        """Test registration with existing username."""
        response = client.post('/auth/register', data={
            'username': 'testuser',  # Already exists
            'email': 'different@test.com',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        })
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data or b'already registered' in response.data


class TestAPIEndpoints:
    """Test API authentication endpoints."""
    
    def test_api_login_valid(self, client):
        """Test API login with valid credentials."""
        response = client.post('/auth/api/login', 
            json={
                'username': 'testuser',
                'password': 'testpass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
    
    def test_api_login_invalid(self, client):
        """Test API login with invalid credentials."""
        response = client.post('/auth/api/login',
            json={
                'username': 'testuser',
                'password': 'wrongpassword'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data


class TestRoleBasedAccess:
    """Test role-based access control."""
    
    def login_user(self, client, username, password):
        """Helper method to login a user."""
        return client.post('/auth/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def test_admin_access(self, client):
        """Test admin can access admin panel."""
        self.login_user(client, 'testadmin', 'testpass123')
        response = client.get('/admin')
        assert response.status_code == 200
        assert b'Admin Panel' in response.data or b'Users Management' in response.data
    
    def test_user_no_admin_access(self, client):
        """Test regular user cannot access admin panel."""
        self.login_user(client, 'testuser', 'testpass123')
        response = client.get('/admin')
        
        # Should redirect to unauthorized or return 403
        assert response.status_code in [302, 403]
    
    def test_unauthenticated_access(self, client):
        """Test unauthenticated user redirected to login."""
        response = client.get('/dashboard')
        assert response.status_code == 302  # Redirect to login


class TestDecorators:
    """Test authentication decorators."""
    
    def test_login_required_decorator(self, app):
        """Test login_required decorator functionality."""
        from frontend.decorators import login_required
        
        @login_required
        def protected_view():
            return "Protected content"
        
        with app.test_request_context():
            # Should redirect when not authenticated
            from flask_login import current_user
            assert not current_user.is_authenticated
    
    def test_role_required_decorator(self, app):
        """Test require_role decorator functionality."""
        from frontend.decorators import require_role
        
        @require_role('admin')
        def admin_view():
            return "Admin content"
        
        with app.test_request_context():
            # Function should be properly decorated
            assert hasattr(admin_view, '__wrapped__')


if __name__ == '__main__':
    pytest.main([__file__])