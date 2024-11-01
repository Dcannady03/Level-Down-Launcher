import os
import hashlib
import json

# Directory to scan
directories_to_scan = ["assets", "_internal"]
manifest = {}

# Function to calculate SHA-256 hash of a file
def calculate_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as file:
        for byte_block in iter(lambda: file.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Generate the manifest
for directory in directories_to_scan:
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            relative_path = os.path.relpath(filepath, start=".")
            manifest[relative_path] = calculate_sha256(filepath)

# Save the new manifest
with open("assets/config/manifest.json", "w") as manifest_file:
    json.dump(manifest, manifest_file, indent=4)

print("New manifest generated successfully!")
