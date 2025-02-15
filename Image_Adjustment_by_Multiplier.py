#!/usr/bin/env python3
import os
from PIL import Image, features
# test 2 is here
# --- Helper Functions ---

def similar_width(w1, w2, tolerance=10):
    """Return True if the two widths differ by no more than tolerance pixels."""
    return abs(w1 - w2) <= tolerance


def vertical_concat(img1, img2):
    """
    Vertically concatenates two images.
    If their widths differ slightly, uses the minimum width.
    """
    width = min(img1.width, img2.width)
    new_im = Image.new('RGB', (width, img1.height + img2.height))
    new_im.paste(img1.crop((0, 0, width, img1.height)), (0, 0))
    new_im.paste(img2.crop((0, 0, width, img2.height)), (0, img1.height))
    return new_im


def split_image(img, desired_height):
    """
    Splits img vertically into pieces.
    Each piece will be (img.width x desired_height), except possibly the last.
    Returns a list of image parts.
    """
    parts = []
    total_height = img.height
    y = 0
    while y < total_height:
        h = min(desired_height, total_height - y)
        part = img.crop((0, y, img.width, y + h))
        parts.append(part)
        y += h
    return parts


def crop_top(img, crop_height):
    """
    Crops the top crop_height pixels from img.
    Returns a tuple (top_crop, leftover).
    """
    top = img.crop((0, 0, img.width, crop_height))
    leftover = img.crop((0, crop_height, img.width, img.height))
    return top, leftover


def safe_open_image(path):
    """
    Safely opens an image and converts it to 'RGB'.
    If an error occurs (e.g. with a problematic WebP image), returns None.
    """
    try:
        with Image.open(path) as img:
            return img.convert('RGB')
    except Exception as e:
        print(f"Warning: Could not open {path}. Skipping it. Error: {e}")
        return None


def save_image(img, path, quality=80, lossless=False):
    """
    Saves the image in WebP format.
    Adjust quality and lossless settings as needed.
    """
    img.save(path, "WEBP", quality=quality, lossless=lossless)
    print(f"Saved: {path}")


# --- Main Processing Function ---

def process_images(input_folder, output_folder):
    """
    Processes images in input_folder according to the 2.5-height rule.
    Saves each finished page immediately in output_folder as WebP.
    """
    os.makedirs(output_folder, exist_ok=True)

    # List image files (supports webp, jpg, jpeg, png)
    files = os.listdir(input_folder)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

    # Sort files numerically if possible (e.g. "1.png", "2.png", …)
    def sort_key(f):
        base = os.path.splitext(f)[0]
        try:
            return int(base)
        except:
            return f

    image_files.sort(key=sort_key)

    page_index = 1
    accumulator = None  # Holds a partially merged image
    tolerance = 10  # Pixel tolerance for width differences

    i = 0  # Index into image_files list

    while i < len(image_files) or accumulator is not None:
        # If there is no accumulator, load the next image.
        if accumulator is None:
            if i >= len(image_files):
                break
            img_path = os.path.join(input_folder, image_files[i])
            img = safe_open_image(img_path)
            i += 1
            if img is None:
                continue  # Skip if image couldn't be opened
            base_width = img.width
            desired_height = int(round(base_width * 2.5))
            # Case 1: Image is too tall – split it.
            if img.height > desired_height:
                parts = split_image(img, desired_height)
                for part in parts[:-1]:
                    out_path = os.path.join(output_folder, f"{page_index}.webp")
                    save_image(part, out_path)
                    page_index += 1
                last_part = parts[-1]
                if last_part.height == desired_height:
                    out_path = os.path.join(output_folder, f"{page_index}.webp")
                    save_image(last_part, out_path)
                    page_index += 1
                    accumulator = None
                else:
                    accumulator = last_part
            # Case 2: Image exactly fits – output it.
            elif img.height == desired_height:
                out_path = os.path.join(output_folder, f"{page_index}.webp")
                save_image(img, out_path)
                page_index += 1
                accumulator = None
            # Case 3: Image is too short – use it as accumulator.
            else:
                accumulator = img
        else:
            base_width = accumulator.width
            desired_height = int(round(base_width * 2.5))
            # Safety check: if accumulator reached or exceeds desired height, split it.
            if accumulator.height >= desired_height:
                if accumulator.height > desired_height:
                    parts = split_image(accumulator, desired_height)
                    for part in parts[:-1]:
                        out_path = os.path.join(output_folder, f"{page_index}.webp")
                        save_image(part, out_path)
                        page_index += 1
                    last_part = parts[-1]
                    if last_part.height == desired_height:
                        out_path = os.path.join(output_folder, f"{page_index}.webp")
                        save_image(last_part, out_path)
                        page_index += 1
                        accumulator = None
                    else:
                        accumulator = last_part
                else:
                    out_path = os.path.join(output_folder, f"{page_index}.webp")
                    save_image(accumulator, out_path)
                    page_index += 1
                    accumulator = None
                continue

            # Try to merge with the next image if available.
            if i < len(image_files):
                next_img_path = os.path.join(input_folder, image_files[i])
                next_img = safe_open_image(next_img_path)
                i += 1
                if next_img is None:
                    continue  # Skip if next image couldn't be opened
                if not similar_width(accumulator.width, next_img.width, tolerance):
                    # Exception: if widths differ significantly, output accumulator as is.
                    out_path = os.path.join(output_folder, f"{page_index}.webp")
                    save_image(accumulator, out_path)
                    page_index += 1
                    accumulator = next_img  # start fresh with next image
                    continue
                else:
                    needed = desired_height - accumulator.height
                    if next_img.height > needed:
                        # Only take the top part of next_img.
                        top_crop, leftover = crop_top(next_img, needed)
                        accumulator = vertical_concat(accumulator, top_crop)
                        out_path = os.path.join(output_folder, f"{page_index}.webp")
                        save_image(accumulator, out_path)
                        page_index += 1
                        accumulator = leftover if leftover.height > 0 else None
                    elif next_img.height == needed:
                        accumulator = vertical_concat(accumulator, next_img)
                        out_path = os.path.join(output_folder, f"{page_index}.webp")
                        save_image(accumulator, out_path)
                        page_index += 1
                        accumulator = None
                    else:
                        # next_img is too short – merge and wait for more.
                        accumulator = vertical_concat(accumulator, next_img)
            else:
                # No more images: output accumulator even if it doesn't meet the rule.
                out_path = os.path.join(output_folder, f"{page_index}.webp")
                save_image(accumulator, out_path)
                page_index += 1
                accumulator = None


def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python Image_Adjustment_by_Multiplier.py path/to/folder")
        sys.exit(1)
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    if not os.path.isdir(input_folder):
        print(f"Error: {input_folder} is not a valid folder.")
        sys.exit(1)

    process_images(input_folder, output_folder)


if __name__ == '__main__':
    main()
