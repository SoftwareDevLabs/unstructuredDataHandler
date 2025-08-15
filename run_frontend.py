#!/usr/bin/env python3
"""
Launch script for the SDLC Core frontend application.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.frontend.app import app

if __name__ == '__main__':
    print("Starting SDLC Core Frontend...")
    print("Access the application at: http://localhost:5000")
    print("Dashboard: http://localhost:5000/")
    print("Settings: http://localhost:5000/settings")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)