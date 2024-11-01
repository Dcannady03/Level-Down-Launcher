# update_manager.py
import os
import json
import requests
import shutil

# Paths to local and remote files
local_manifest_path = "assets/config/manifest.json"
previous_manifest_path = "assets/config/previous_manifest.json"
version_file_path = "assets/config/version.json"
temp_folder = "temp_update"  # Temporary folder for downloads

manifest_url = "https://raw.githubusercontent.com/Dcannady03/Level-Down-Launcher/update/update_files/assets/config/manifest.json"
base_file_url = "https://raw.githubusercontent.com/Dcannady03/Level-Down-Launcher/update/update_files"
version_url = "https://raw.githubusercontent.com/Dcannady03/Level-Down-Launcher/update/update_files/assets/config/version.json"

# Load JSON file
def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as file:
            return json.load(file)
    return {}

# Save JSON file
def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)

# Load version info
def get_local_version():
    return load_json(version_file_path).get("version", "0.0")

def get_remote_version():
    response = requests.get(version_url)
    if response.status_code == 200:
        return response.json().get("version", "0.0")
    else:
        print("Failed to fetch remote version.")
        return None

# Check for changed files based on manifest comparison
def get_changed_files(current_manifest, previous_manifest):
    changed_files = []
    for filepath, current_hash in current_manifest.items():
        previous_hash = previous_manifest.get(filepath)
        if current_hash != previous_hash:
            changed_files.append(filepath)
    return changed_files

# Download file from server to temp folder
def download_file(relative_path):
    file_url = f"{base_file_url}/{relative_path}"
    temp_path = os.path.join(temp_folder, relative_path)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(temp_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {relative_path} to temp.")
    else:
        print(f"Failed to download {relative_path}")

# Replace old files with new ones from temp
def replace_files_from_temp():
    for root, _, files in os.walk(temp_folder):
        for file in files:
            temp_file_path = os.path.join(root, file)
            relative_path = os.path.relpath(temp_file_path, temp_folder)
            final_path = os.path.join(os.getcwd(), relative_path)
            os.makedirs(os.path.dirname(final_path), exist_ok=True)
            shutil.move(temp_file_path, final_path)
            print(f"Replaced {relative_path}")

    # Clean up the temporary folder after moving files
    shutil.rmtree(temp_folder)

# Main update function
def check_for_update():
    local_version = get_local_version()
    remote_version = get_remote_version()

    if not remote_version:
        return False

    if remote_version > local_version:
        print(f"New version {remote_version} available! Updating...")

        # Step 1: Download and save the remote manifest
        response = requests.get(manifest_url)
        if response.status_code == 200:
            remote_manifest = response.json()
            save_json(local_manifest_path, remote_manifest)
        else:
            print("Failed to download the remote manifest.")
            return False

        # Load previous manifest for comparison
        previous_manifest = load_json(previous_manifest_path) if os.path.exists(previous_manifest_path) else {}

        # Step 2: Get changed files
        changed_files = get_changed_files(remote_manifest, previous_manifest)

        # Step 3: Download each changed file to the temporary folder
        for file in changed_files:
            download_file(file)

        # Step 4: Replace old files with new ones from temp folder
        replace_files_from_temp()

        # Step 5: Update version.json and previous manifest
        save_json(version_file_path, {"version": remote_version})
        save_json(previous_manifest_path, remote_manifest)

        print("Update complete.")
        return True
    else:
        print("Application is up to date.")
        return False



