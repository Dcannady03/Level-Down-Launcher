import json
import os

SETTINGS_FILE = 'assets/config/settings.json'

def load_settings():
    """Loads settings from the JSON file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as file:
            return json.load(file)
    else:
        return {
            "theme": "dark",  # Default theme
            "resolution_width": "1920",
            "resolution_height": "1080",
            "language": "2"
        }

def save_settings(settings):
    """Saves settings to the JSON file."""
    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
    with open(SETTINGS_FILE, 'w') as file:
        json.dump(settings, file, indent=4)

