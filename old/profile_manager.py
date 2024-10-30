import configparser
import os

def load_profile(profile_path):
    """Loads the profile from the given .ini file."""
    config = configparser.ConfigParser()
    if os.path.exists(profile_path):
        config.read(profile_path)
    else:
        raise FileNotFoundError(f"Profile {profile_path} not found.")
    
    # Return necessary settings (resolution, language)
    resolution_width = config.get("ffxi.registry", "0001", fallback="1920")
    resolution_height = config.get("ffxi.registry", "0002", fallback="1080")
    language = config.get("ashita.language", "playonline", fallback="2")
    
    return {
        "resolution_width": resolution_width,
        "resolution_height": resolution_height,
        "language": language
    }

def save_profile(profile_path, settings):
    """Saves the modified profile settings to the given .ini file."""
    config = configparser.ConfigParser()
    if os.path.exists(profile_path):
        config.read(profile_path)
    else:
        raise FileNotFoundError(f"Profile {profile_path} not found.")
    
    # Update the settings
    config.set("ffxi.registry", "0001", settings.get("resolution_width", "1920"))
    config.set("ffxi.registry", "0002", settings.get("resolution_height", "1080"))
    config.set("ashita.language", "playonline", settings.get("language", "2"))
    
    # Write the changes back to the file
    with open(profile_path, 'w') as configfile:
        config.write(configfile)

