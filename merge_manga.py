#!/usr/bin/env python3
import os
import sys
import shutil
import argparse
import re


def parse_chapter_info(name):
    """
    Examines a folder (chapter) name and returns a tuple:
      (priority, volume, chapter_number, original_name)
    Lower tuple values come first in sorting.

    The priority values used here are:
      1  → Normal chapters (names containing "chapter", "ch", or "episode")
      3  → Prologue (when not accompanied by a chapter number)
      4  → Epilogue or Creator's Note
      5  → Side story
     10  → Fallback for unknown naming

    Special handling:
      - If the folder name starts with "chapter", "ch", or "episode",
        we ignore any volume information (forcing volume = 1).
      - Otherwise, if a volume appears in the name (like "Vol. 2" or "Volume 2"),
        it is extracted.
    """
    lower = name.lower().strip()

    # Special case: oneshot is treated as a normal chapter 1.
    if lower.startswith("oneshot"):
        return (1, 1, 1, name)

    # Handle special cases first:
    if lower.startswith("epilogue"):
        chap_match = re.search(r'epilogue\s*\.?\s*(\d+(\.\d+)?)', lower)
        chap = float(chap_match.group(1)) if chap_match else 0
        # For epilogues, we ignore volume info (or you can keep it, if desired)
        return (4, 1, chap, name)

    if lower.startswith("creator's note"):
        return (6, 1, 0, name)

    if lower.startswith("prologue"):
        chap_match = re.search(r'prologue\s*\.?\s*(\d+(\.\d+)?)', lower)
        chap = float(chap_match.group(1)) if chap_match else 0
        return (3, 1, chap, name)

    if lower.startswith("side"):
        chap_match = re.search(r'side(?:\s*story)?\.?\s*(\d+(\.\d+)?)', lower)
        chap = float(chap_match.group(1)) if chap_match else 0
        return (5, 1, chap, name)

    # For normal chapters, if the folder name starts with a chapter keyword,
    # we ignore any volume info.
    if lower.startswith("chapter") or lower.startswith("ch") or lower.startswith("episode"):
        volume = 1
    else:
        # Otherwise, try to extract a volume number (e.g. "Vol. 2" or "Volume 2")
        vol_match = re.search(r'vol(?:ume)?\.?\s*(\d+)', lower)
        volume = int(vol_match.group(1)) if vol_match else 1

    # Look for normal chapter keywords: "chapter", "ch", or "episode"
    chap_match = re.search(r'(?:chapter|ch|episode)\s*\.?\s*(\d+(\.\d+)?)', lower)
    if chap_match:
        try:
            chap = float(chap_match.group(1))
        except ValueError:
            chap = 0
        return (1, volume, chap, name)

    # Fallback: if we cannot match any known pattern, push it to the end.
    return (10, volume, 0, name)


def main():
    parser = argparse.ArgumentParser(
        description="Merge manga chapter images into one final folder with continuous numbering."
    )
    parser.add_argument("folder", help="Path to the folder containing chapter subdirectories")
    args = parser.parse_args()

    base_folder = os.path.abspath(args.folder)

    # Create a destination folder called "final" within the base folder.
    destination_folder = os.path.join(base_folder, "final")
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
        print(f"Created destination folder: {destination_folder}")

    # List all subdirectories (chapter folders) except for the destination folder.
    chapters = [
        d for d in os.listdir(base_folder)
        if os.path.isdir(os.path.join(base_folder, d)) and d.lower() != "final"
    ]

    # Sort the chapters using our custom sort key.
    chapters.sort(key=lambda d: parse_chapter_info(d))

    print("Sorted chapters (with sort keys):")
    for idx, ch in enumerate(chapters, 1):
        print(f"{idx}. {ch} -> {parse_chapter_info(ch)}")

    # Ask for confirmation before proceeding.
    # confirm = input("\nDo you want to continue with merging these chapters? (Y/n): ")
    # if confirm.lower() not in ("", "y", "yes"):
    #     print("Operation cancelled by user.")
    #     sys.exit(0)

    current_num = 1  # running counter for the merged image filenames

    # Process each chapter folder in sorted order.
    for chapter in chapters:
        chapter_path = os.path.join(base_folder, chapter)
        print(f"\nProcessing chapter folder: {chapter_path}")

        # List image files (adjust the extensions if needed)
        images = [
            f for f in os.listdir(chapter_path)
            if os.path.isfile(os.path.join(chapter_path, f)) and
               f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.jxl', '.avif'))
        ]

        # Sort the images based on any numeric portion in the filename.
        images.sort(key=lambda f: float(re.search(r'\d+(\.\d+)?', os.path.splitext(f)[0]).group(0))
        if re.search(r'\d+(\.\d+)?', os.path.splitext(f)[0])
        else 0)

        # Copy the images to the final folder with new continuous numbering.
        for image in images:
            old_path = os.path.join(chapter_path, image)
            ext = os.path.splitext(image)[1]  # get the extension (includes the dot)
            new_filename = f"{current_num}{ext}"
            new_path = os.path.join(destination_folder, new_filename)
            shutil.copy2(old_path, new_path)  # Copy the file (preserving metadata)
            print(f"Copied: {old_path}  -->  {new_path}")
            current_num += 1

    print("\nAll images have been merged successfully.")


if __name__ == "__main__":
    main()
