"""
Database models for user authentication and role management.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship to roles
    user_roles = db.relationship('UserRole', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role_name):
        """Check if user has a specific role."""
        return self.user_roles.join(Role).filter(Role.name == role_name).count() > 0
    
    def get_roles(self):
        """Get all roles for this user."""
        return [ur.role.name for ur in self.user_roles]
    
    def add_role(self, role):
        """Add a role to this user."""
        if not self.has_role(role.name):
            user_role = UserRole(user_id=self.id, role_id=role.id)
            db.session.add(user_role)
            return True
        return False
    
    def remove_role(self, role):
        """Remove a role from this user."""
        user_role = self.user_roles.join(Role).filter(Role.name == role.name).first()
        if user_role:
            db.session.delete(user_role)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Role(db.Model):
    """Role model for role-based access control."""
    
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to users
    user_roles = db.relationship('UserRole', backref='role', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Role {self.name}>'


class UserRole(db.Model):
    """Association table for many-to-many relationship between users and roles."""
    
    __tablename__ = 'user_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Ensure unique user-role combinations
    __table_args__ = (db.UniqueConstraint('user_id', 'role_id'),)
    
    def __repr__(self):
        return f'<UserRole user_id={self.user_id} role_id={self.role_id}>'


def init_default_roles():
    """Initialize default roles in the database."""
    default_roles = [
        {'name': 'admin', 'description': 'Full system administrator access'},
        {'name': 'user', 'description': 'Standard user access'},
        {'name': 'moderator', 'description': 'Content moderation access'},
        {'name': 'analyst', 'description': 'Data analysis and reporting access'},
        {'name': 'developer', 'description': 'Development and API access'},
    ]
    
    for role_data in default_roles:
        existing_role = Role.query.filter_by(name=role_data['name']).first()
        if not existing_role:
            role = Role(name=role_data['name'], description=role_data['description'])
            db.session.add(role)
    
    db.session.commit()