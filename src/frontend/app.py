#!/usr/bin/env python3
"""
SDLC Core Frontend Application Entry Point

This script starts the Flask web application with authentication and role management.
"""
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from frontend.auth import create_app
from frontend.models import db, User, Role, UserRole, init_default_roles


def create_admin_user(app):
    """Create a default admin user if none exists."""
    with app.app_context():
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_role = Role.query.filter_by(name='admin').first()
            if admin_role:
                admin_user = User(
                    username='admin',
                    email='admin@sdlccore.com'
                )
                admin_user.set_password('admin123')  # Change this in production!
                db.session.add(admin_user)
                db.session.flush()  # Get user ID before adding role
                
                user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
                db.session.add(user_role)
                db.session.commit()
                print("✓ Default admin user created (username: admin, password: admin123)")
            else:
                print("✗ Admin role not found. Cannot create admin user.")
        else:
            print("✓ Admin user already exists")


def main():
    """Main entry point for the application."""
    print("🚀 Starting SDLC Core Frontend Infrastructure...")
    
    # Set environment variables if not set
    if not os.getenv('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'dev-secret-key-change-in-production'
        print("⚠️  Using default SECRET_KEY. Change in production!")
    
    if not os.getenv('DATABASE_URL'):
        db_path = Path(__file__).parent / 'sdlc_core.db'
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path.absolute()}'
        print(f"📁 Using SQLite database: {db_path.absolute()}")
    
    # Create the Flask app
    app = create_app()
    
    # Create admin user
    create_admin_user(app)
    
    # Print available routes
    print("\n📋 Available Routes:")
    with app.app_context():
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print(f"  {rule.endpoint:30} {methods:10} {rule.rule}")
    
    print("\n🌐 Frontend Infrastructure Setup Complete!")
    print("   • Role-based authentication system ✓")
    print("   • User management interface ✓")
    print("   • Admin panel ✓")
    print("   • REST API endpoints ✓")
    print("   • Responsive web interface ✓")
    
    print(f"\n🔗 Access the application at: http://localhost:5000")
    print("   • Home: http://localhost:5000/")
    print("   • Login: http://localhost:5000/auth/login")
    print("   • Register: http://localhost:5000/auth/register")
    print("   • Admin: http://localhost:5000/admin (admin role required)")
    
    print("\n🔑 Default Admin Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   ⚠️  Please change the admin password after first login!")
    
    # Run the application
    debug = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    
    print(f"\n🏃 Running on port {port} (debug={'on' if debug else 'off'})")
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()