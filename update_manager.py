import os
import hashlib
import json
import requests

# Paths
manifest_url = "https://github.com/Dcannady03/Level-Down-Launcher/tree/main/assets/configmanifest.json"  # URL of remote manifest
base_file_url = "https://yourserver.com/path/to/files"         # URL where individual files are stored
local_manifest_path = "assets/config/manifest.json"
directories_to_verify = ["_internal", "assets"]

# Excluded files
excluded_files = ["assets/settings.json"]

# Load the remote manifest
response = requests.get(manifest_url)
if response.status_code == 200:
    remote_manifest = response.json()
else:
    print("Failed to download the remote manifest.")
    exit()

# Load the local manifest
with open(local_manifest_path, "r") as manifest_file:
    local_manifest = json.load(manifest_file)

# Function to calculate SHA-256 hash of a file
def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Function to download a file
def download_file(relative_path):
    file_url = f"{base_file_url}/{relative_path}"
    local_path = os.path.join(os.getcwd(), relative_path)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    # Download and save the file
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(local_path, "wb") as file:
            file.write(response.content)
        print(f"Downloaded {relative_path}")
    else:
        print(f"Failed to download {relative_path}")

# Check each file in the remote manifest and update if needed
for relative_path, remote_hash in remote_manifest.items():
    # Skip excluded files
    if f"assets/{relative_path}" in excluded_files:
        continue

    local_path = os.path.join(relative_path)
    if os.path.exists(local_path):
        local_hash = calculate_sha256(local_path)
        if local_hash != remote_hash:
            print(f"Updating {relative_path}")
            download_file(relative_path)
    else:
        print(f"Downloading missing file {relative_path}")
        download_file(relative_path)

# Update local manifest after download
with open(local_manifest_path, "w") as manifest_file:
    json.dump(remote_manifest, manifest_file, indent=4)

print("Update process complete.")

