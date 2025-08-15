"""
Tests for the SDLC Core frontend application.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import patch

# Add the parent directory to sys.path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, load_config, save_config, DEFAULT_CONFIG


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(DEFAULT_CONFIG, f)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)


class TestConfigManagement:
    """Test configuration loading and saving."""
    
    def test_load_default_config(self):
        """Test that default config is returned when no file exists."""
        with patch('app.CONFIG_FILE', '/nonexistent/file.json'):
            config = load_config()
            assert config == DEFAULT_CONFIG
    
    def test_save_and_load_config(self, temp_config_file):
        """Test saving and loading configuration."""
        test_config = {
            "selected_backend": "anthropic",
            "backends": {
                "openai": {"name": "OpenAI", "api_key": "test-key", "enabled": True},
                "anthropic": {"name": "Anthropic", "api_key": "test-key-2", "enabled": False}
            }
        }
        
        with patch('app.CONFIG_FILE', temp_config_file):
            assert save_config(test_config)
            loaded_config = load_config()
            assert loaded_config == test_config


class TestRoutes:
    """Test Flask routes."""
    
    def test_index_route(self, client):
        """Test the main dashboard route."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'LLM Infrastructure Dashboard' in response.data
    
    def test_settings_route(self, client):
        """Test the settings page route."""
        response = client.get('/settings')
        assert response.status_code == 200
        assert b'LLM Backend Settings' in response.data
    
    def test_get_config_api(self, client):
        """Test the GET /api/config endpoint."""
        response = client.get('/api/config')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'selected_backend' in data
        assert 'backends' in data
    
    def test_update_config_api(self, client, temp_config_file):
        """Test the POST /api/config endpoint."""
        test_config = {
            "selected_backend": "anthropic",
            "backends": {"test": {"name": "Test", "enabled": True}}
        }
        
        with patch('app.CONFIG_FILE', temp_config_file):
            response = client.post('/api/config', 
                                   data=json.dumps(test_config),
                                   content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    def test_select_backend_api(self, client, temp_config_file):
        """Test the POST /api/backend/select endpoint."""
        with patch('app.CONFIG_FILE', temp_config_file):
            # Test valid backend selection
            response = client.post('/api/backend/select',
                                   data=json.dumps({"backend": "anthropic"}),
                                   content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            # Test invalid backend selection
            response = client.post('/api/backend/select',
                                   data=json.dumps({"backend": "invalid"}),
                                   content_type='application/json')
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False


class TestFrontendIntegration:
    """Test frontend integration scenarios."""
    
    def test_backend_switching_workflow(self, client, temp_config_file):
        """Test the complete backend switching workflow."""
        with patch('app.CONFIG_FILE', temp_config_file):
            # Get initial config
            response = client.get('/api/config')
            initial_config = json.loads(response.data)
            initial_backend = initial_config['selected_backend']
            
            # Switch to a different backend
            new_backend = 'anthropic' if initial_backend == 'openai' else 'openai'
            response = client.post('/api/backend/select',
                                   data=json.dumps({"backend": new_backend}),
                                   content_type='application/json')
            assert response.status_code == 200
            
            # Verify the switch took effect
            response = client.get('/api/config')
            updated_config = json.loads(response.data)
            assert updated_config['selected_backend'] == new_backend
    
    def test_settings_persistence(self, client, temp_config_file):
        """Test that settings persist across requests."""
        test_config = {
            "selected_backend": "anthropic",
            "backends": {
                "openai": {
                    "name": "OpenAI",
                    "description": "OpenAI's GPT models",
                    "api_key": "test-openai-key",
                    "model": "gpt-4",
                    "enabled": True
                },
                "anthropic": {
                    "name": "Anthropic", 
                    "description": "Anthropic's Claude models",
                    "api_key": "test-anthropic-key",
                    "model": "claude-3-opus",
                    "enabled": True
                }
            }
        }
        
        with patch('app.CONFIG_FILE', temp_config_file):
            # Save configuration
            response = client.post('/api/config',
                                   data=json.dumps(test_config),
                                   content_type='application/json')
            assert response.status_code == 200
            
            # Verify persistence by getting config again
            response = client.get('/api/config')
            retrieved_config = json.loads(response.data)
            assert retrieved_config == test_config


if __name__ == '__main__':
    pytest.main([__file__, '-v'])