#!/usr/bin/env python3
"""
create_zip.py - Create a clean zip file of the capstone project
Excludes cache files and temporary files.
"""

import os
import zipfile

def make_capstone_zip(output_zip="capstone_project.zip"):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    zip_path = os.path.join(parent_dir, output_zip)

    # Patterns to ignore
    ignore_patterns = ["__pycache__", ".DS_Store", ".git"]

    print(f"Creating zip file at: {zip_path}")
    count = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(current_dir):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_patterns]
            for file in files:
                if any(p in file for p in ignore_patterns):
                    continue
                file_path = os.path.join(root, file)
                # Archive name relative to parent directory
                arcname = os.path.relpath(file_path, parent_dir)
                zipf.write(file_path, arcname)
                count += 1

    size_kb = os.path.getsize(zip_path) / 1024
    print(f"✅ Success! Packed {count} files into '{zip_path}' ({size_kb:.1f} KB).")
    return zip_path

if __name__ == "__main__":
    make_capstone_zip()
