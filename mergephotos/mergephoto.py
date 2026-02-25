#!/usr/bin/env python3

import argparse
import sys
from PIL import Image


def validate_format(path: str):
    lower = path.lower()
    if not (lower.endswith(".png") or lower.endswith(".jpg") or lower.endswith(".jpeg")):
        raise ValueError(f"Unsupported format: {path}. Only PNG and JPEG are supported.")


def merge_images(left_path: str, right_path: str, output_path: str):
    # Validate formats
    validate_format(left_path)
    validate_format(right_path)
    validate_format(output_path)

    # Open images
    left_img = Image.open(left_path)
    right_img = Image.open(right_path)

    # Convert to RGB to avoid mode mismatch (especially RGBA → JPEG)
    if left_img.mode != "RGB":
        left_img = left_img.convert("RGB")
    if right_img.mode != "RGB":
        right_img = right_img.convert("RGB")

    left_width, left_height = left_img.size
    right_width, right_height = right_img.size

    final_width = left_width + right_width
    final_height = max(left_height, right_height)

    # Create new blank image (black background)
    merged = Image.new("RGB", (final_width, final_height), (0, 0, 0))

    # Paste images
    merged.paste(left_img, (0, 0))
    merged.paste(right_img, (left_width, 0))

    # Save
    merged.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="Merge two images horizontally.")
    parser.add_argument("-left", required=True, help="Left image file (png or jpeg)")
    parser.add_argument("-right", required=True, help="Right image file (png or jpeg)")
    parser.add_argument("-o", required=True, help="Output image file (png or jpeg)")

    args = parser.parse_args()

    try:
        merge_images(args.left, args.right, args.o)
        print(f"Successfully created merged image: {args.o}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

