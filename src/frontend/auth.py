"""
Main Flask application factory and authentication blueprint.
"""
import os
from datetime import datetime
from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import LoginManager, login_user, logout_user, current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect, validate_csrf
from werkzeug.exceptions import BadRequest

from .models import db, User, Role, UserRole, init_default_roles
from .forms import LoginForm, RegisterForm
from .decorators import login_required, require_role, admin_required


def create_app(config=None):
    """Application factory pattern."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///sdlc_core.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    
    if config:
        app.config.update(config)
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    csrf = CSRFProtect(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    
    # Create tables and default data
    with app.app_context():
        db.create_all()
        init_default_roles()
    
    return app


# Authentication Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated.', 'error')
                return render_template('auth/login.html', form=form)
            
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            
            flash('Logged in successfully!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | 
            (User.email == form.email.data)
        ).first()
        
        if existing_user:
            flash('Username or email already exists.', 'error')
            return render_template('auth/register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        # Assign default role
        default_role = Role.query.filter_by(name='user').first()
        if default_role:
            db.session.add(user)
            db.session.flush()  # Get user ID before adding role
            user_role = UserRole(user_id=user.id, role_id=default_role.id)
            db.session.add(user_role)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/unauthorized')
def unauthorized():
    """Unauthorized access page."""
    return render_template('auth/unauthorized.html'), 403


# API Authentication Routes
@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """API login endpoint."""
    # Skip CSRF validation for API endpoints
    try:
        data = request.get_json()
    except BadRequest:
        return jsonify({'error': 'Invalid JSON'}), 400
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if user and user.check_password(data['password']):
        if not user.is_active:
            return jsonify({'error': 'Account deactivated'}), 403
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'roles': user.get_roles()
            }
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/api/user/profile')
@login_required
def api_user_profile():
    """API endpoint to get current user profile."""
    return jsonify({
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'roles': current_user.get_roles(),
            'is_active': current_user.is_active,
            'created_at': current_user.created_at.isoformat(),
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None
        }
    })


# Main Blueprint
main_bp = Blueprint('main', __name__, template_folder='templates')


@main_bp.route('/')
def index():
    """Main index page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    return render_template('dashboard.html', user=current_user)


@main_bp.route('/admin')
@admin_required
def admin():
    """Admin panel."""
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin.html', users=users, roles=roles)


@main_bp.route('/api/admin/users')
@admin_required
def api_admin_users():
    """API endpoint to get all users (admin only)."""
    users = User.query.all()
    return jsonify({
        'users': [
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_active': user.is_active,
                'roles': user.get_roles(),
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
            for user in users
        ]
    })


@main_bp.route('/api/admin/roles')
@admin_required
def api_admin_roles():
    """API endpoint to get all roles (admin only)."""
    roles = Role.query.all()
    return jsonify({
        'roles': [
            {
                'id': role.id,
                'name': role.name,
                'description': role.description,
                'created_at': role.created_at.isoformat()
            }
            for role in roles
        ]
    })