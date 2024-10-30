import os
import hashlib
import json

# Directories to scan
directories_to_scan = ["_internal", "assets"]
# Path to save the manifest
manifest_path = "assets/config/manifest.json"
# File to exclude from the manifest
exclude_files = ["assets/config/settings.json"]

# Function to calculate SHA-256 hash of a file
def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Generate the manifest
manifest = {}
for directory in directories_to_scan:
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            # Skip excluded files
            if filepath in exclude_files:
                continue
            # Use relative path for manifest entries
            relative_path = os.path.relpath(filepath, start=directory)
            manifest[relative_path] = calculate_sha256(filepath)

# Save the manifest to JSON file
with open(manifest_path, "w") as manifest_file:
    json.dump(manifest, manifest_file, indent=4)

print("Manifest generated successfully, excluding settings.json!")
