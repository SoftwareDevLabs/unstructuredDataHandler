"""
Frontend web application for SDLC_core LLM infrastructure settings.
Provides a GUI interface for selecting and configuring LLM backends.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from typing import Dict, Any

app = Flask(__name__)

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'settings.json')

# Default configuration
DEFAULT_CONFIG = {
    "selected_backend": "openai",
    "backends": {
        "openai": {
            "name": "OpenAI",
            "description": "OpenAI's GPT models (GPT-3.5, GPT-4, etc.)",
            "api_key": "",
            "model": "gpt-3.5-turbo",
            "enabled": True
        },
        "anthropic": {
            "name": "Anthropic",
            "description": "Anthropic's Claude models",
            "api_key": "",
            "model": "claude-3-sonnet-20240229",
            "enabled": True
        }
    }
}

def load_config() -> Dict[str, Any]:
    """Load configuration from file or return default."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file."""
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

@app.route('/')
def index():
    """Main dashboard."""
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/settings')
def settings():
    """Settings page for backend configuration."""
    config = load_config()
    return render_template('settings.html', config=config)

@app.route('/api/config', methods=['GET'])
def get_config():
    """API endpoint to get current configuration."""
    config = load_config()
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """API endpoint to update configuration."""
    try:
        new_config = request.json
        if save_config(new_config):
            return jsonify({"success": True, "message": "Configuration updated successfully"})
        else:
            return jsonify({"success": False, "message": "Failed to save configuration"}), 500
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/backend/select', methods=['POST'])
def select_backend():
    """API endpoint to select a backend."""
    try:
        data = request.json
        backend = data.get('backend')
        
        config = load_config()
        if backend in config['backends']:
            config['selected_backend'] = backend
            if save_config(config):
                return jsonify({"success": True, "message": f"Backend switched to {backend}"})
        
        return jsonify({"success": False, "message": "Invalid backend"}), 400
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)