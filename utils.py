import json
import os

CONFIG_PATH = "assets/config/config.json"
VERSION_PATH = "assets/config/version.json"

def load_version():
    """Load the current version from version.json."""
    try:
        with open(VERSION_PATH, 'r') as file:
            version_data = json.load(file)
        return version_data.get("launcher_version", "1.0.0")
    except Exception as e:
        print(f"Error loading version: {e}")
        return "1.0.0"

def save_version(new_version):
    """Save a new version to version.json."""
    try:
        with open(VERSION_PATH, 'r') as file:
            version_data = json.load(file)

        version_data["launcher_version"] = new_version

        with open(VERSION_PATH, 'w') as file:
            json.dump(version_data, file, indent=4)
        print("Version updated successfully.")
    except Exception as e:
        print(f"Error updating version: {e}")

def load_config():
    """Load the configuration from config.json."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading configuration: {e}")
    return {
        "ashita_exe": "",
        "windower_exe": "",
        "xi_loader_exe": "assets/config/xiLoader.exe"
    }

def save_config(config):
    """Save configuration to config.json."""
    try:
        with open(CONFIG_PATH, 'w') as file:
            json.dump(config, file, indent=4)
        print("Configuration saved successfully.")
    except Exception as e:
        print(f"Error saving configuration: {e}")
