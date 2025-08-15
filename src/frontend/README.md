# Frontend for SDLC Core LLM Infrastructure

This frontend application provides a web-based GUI for managing LLM backend settings in the SDLC Core system.

## Features

- **Backend Selection**: Choose between different LLM providers (OpenAI, Anthropic, etc.)
- **Configuration Management**: Set API keys, models, and other backend-specific settings
- **Visual Interface**: Clean, responsive web interface with real-time updates
- **Settings Persistence**: Configuration is saved locally and persists across sessions

## Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to `http://localhost:5000`

## Usage

### Dashboard
- View the currently active LLM backend
- See all available backends
- Quick-switch between backends

### Settings Page
- Configure API keys for each backend
- Set preferred models
- Enable/disable specific backends
- Save and persist configuration changes

## Configuration

The application stores settings in `config/settings.json`. This file is automatically created with default settings on first run.

Default backends supported:
- **OpenAI**: GPT models (GPT-3.5, GPT-4, etc.)
- **Anthropic**: Claude models

## API Endpoints

- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `POST /api/backend/select` - Switch active backend

## File Structure

```
frontend/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html        # Dashboard page
│   └── settings.html     # Settings configuration page
└── config/
    └── settings.json     # Persistent configuration (auto-generated)
```