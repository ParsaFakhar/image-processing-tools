#!/usr/bin/env python3
import os
import sys
import subprocess

def main(collection_path):
    if not os.path.isdir(collection_path):
        print(f"Error: '{collection_path}' is not a valid directory.")
        sys.exit(1)

    # Loop through each subdirectory in the collection folder
    for subdir in os.listdir(collection_path):
        subdir_path = os.path.join(collection_path, subdir)
        if not os.path.isdir(subdir_path):
            continue  # Skip files

        # Define path to the 'final' folder inside this subdirectory
        final_folder = os.path.join(subdir_path, "final")
        if not os.path.isdir(final_folder):
            print(f"Warning: 'final' folder not found in '{subdir_path}'. Skipping.")
            continue

        # Create the 'output' folder next to the 'final' folder if it doesn't exist
        output_folder = os.path.join(subdir_path, "output")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            print(f"Created 'output' folder at: {output_folder}")
        else:
            print(f"'output' folder already exists at: {output_folder}")

        # Build the command to run DeepSeek_Splitter.py with the required arguments
        cmd = ["python3", "/Users/johanvillibert/PycharmProjects/image-processing-tools/Image_Adjustment_by_Multiplier.py", final_folder, output_folder]
        print(f"Running: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: Image_Adjustment_by_Multiplier.py failed in '{subdir_path}' with error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python Run_ImageMultiplier_on_ALL_Folders.py /path/to/collection")
        sys.exit(1)

    collection_dir = sys.argv[1]
    main(collection_dir)
