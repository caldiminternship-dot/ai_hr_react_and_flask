#!/usr/bin/env python3
"""
Clear Python cache files to ensure code changes are reflected
Run this script whenever you make changes to Python files
"""
import os
import shutil

def clear_pycache():
    """Remove all __pycache__ directories and .pyc files"""
    removed_count = 0

    print("Clearing Python cache...")

    # Walk through directory
    for root, dirs, files in os.walk('.'):
        # Skip .git and other hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        # Remove __pycache__ directories
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_path)
                print(f"Removed: {cache_path}")
                removed_count += 1
            except Exception as e:
                print(f"Error removing {cache_path}: {e}")

        # Remove .pyc files
        for file in files:
            if file.endswith('.pyc'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")

    print(f"\nCache cleared! Removed {removed_count} cached files/directories.")
    print("Now restart your Streamlit server for changes to take effect.")

if __name__ == "__main__":
    clear_pycache()
