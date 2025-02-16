#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(
        description="Batch process manga folders using merger_manga.py"
    )
    parser.add_argument(
        "folder",
        help="Path to the folder containing individual manga subfolders"
    )
    args = parser.parse_args()

    # Convert to absolute path and check if it exists
    collection_folder = os.path.abspath(args.folder)
    if not os.path.isdir(collection_folder):
        print(f"Error: {collection_folder} is not a directory.")
        sys.exit(1)

    # List all subdirectories (each representing a manga)
    manga_folders = [
        os.path.join(collection_folder, d)
        for d in os.listdir(collection_folder)
        if os.path.isdir(os.path.join(collection_folder, d))
    ]
    manga_folders.sort()

    # Determine the path to merger_manga.py (assumed to be in the same directory as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    merger_script = os.path.join(script_dir, "merge_manga.py")
    if not os.path.exists(merger_script):
        print(f"Error: {merger_script} not found.")
        sys.exit(1)

    # Process each manga folder by calling merger_manga.py with its path as argument
    for manga in manga_folders:
        print(f"\nProcessing manga folder: {manga}")
        # Use sys.executable so the same Python interpreter is used.
        result = subprocess.run([sys.executable, merger_script, manga])
        if result.returncode != 0:
            print(f"Error processing {manga}. Skipping to next folder.")
        else:
            print(f"Finished processing: {manga}")

if __name__ == "__main__":
    main()
