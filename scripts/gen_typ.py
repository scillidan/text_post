# Authors: GLM-4.5🧙‍, scillidan🤡

import sys
import argparse
import shutil
import os
from pathlib import Path


def generate_typ(filename, fonts):
    typs_dir = Path("typs")
    typs_dir.mkdir(exist_ok=True)

    # Ensure pdfs directory exists
    pdfs_dir = Path("pdfs")
    pdfs_dir.mkdir(exist_ok=True)

    # Ensure jpgs directory exists
    jpgs_dir = Path("jpgs")
    jpgs_dir.mkdir(exist_ok=True)

    # Create images directory in project if it doesn't exist
    images_dir = Path("images")
    images_dir.mkdir(exist_ok=True)

    md_path = Path(f"{filename}.md")

    if not md_path.exists():
        print(f"Error: Markdown file not found for {filename}")
        sys.exit(1)

    # Process markdown: convert CDN links to local images and copy them
    with open(md_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    # Find all CDN images (with or without alt text)
    import re

    # Extract all CDN image references
    all_images = set()

    # Empty alt text: ![](https://scillidan.github.io/cdn_image_post/filename.webp)
    all_images.update(
        re.findall(
            r"!\[\]\(https://scillidan\.github\.io/cdn_image_post/(.+?)\.\w+\)",
            md_content,
        )
    )

    # With alt text: ![alt](https://scillidan.github.io/cdn_image_post/filename.webp)
    for match in re.findall(
        r"!\[([^\]]*)\]\(https://scillidan\.github\.io/cdn_image_post/(.+?)\.\w+\)",
        md_content,
    ):
        if isinstance(match, tuple):
            all_images.add(match[1])

    # Copy image files to project images directory
    # Supported formats: jpg, jpeg, png, gif, svg, webp
    supported_formats = ["jpg", "jpeg", "png", "gif", "svg", "webp"]

    for image_base_name in all_images:
        copied = False
        for ext in supported_formats:
            source_filename = f"{image_base_name}.{ext}"
            source_path = Path("../cdn_image_post") / source_filename
            dest_path = images_dir / source_filename

            if source_path.exists():
                if not dest_path.exists():
                    shutil.copy(source_path, dest_path)
                    print(f"Copied image: {source_filename}")
                copied = True
                break

        if not copied:
            print(f"Warning: Could not find image for {image_base_name}")

    # Convert CDN URLs to local image paths
    def replace_cdn_url(match):
        alt_text = match.group(1) if match.group(1) else ""
        image_name = match.group(2)

        # Find the actual file extension for this image
        for ext in supported_formats:
            test_path = images_dir / f"{image_name}.{ext}"
            if test_path.exists():
                return f"![{alt_text}](images/{image_name}.{ext})"

        # Remove image if not found locally (to avoid Windows path errors)
        return ""

    # Replace both empty and alt text versions
    md_content_local = re.sub(
        r"!\[([^\]]*)\]\(https://scillidan\.github\.io/cdn_image_post/(.+?)\.\w+\)",
        replace_cdn_url,
        md_content,
    )

    # Clean up empty lines left by removed images
    import re as re2

    md_content_local = re2.sub(r"\n{3,}", "\n\n", md_content_local)

    # Write processed markdown to a new file
    md_processed_path = typs_dir.parent / f"{filename}-processed.md"
    with open(md_processed_path, "w", encoding="utf-8") as f:
        f.write(md_content_local)

    # Instead of copying images, create symbolic link in cmarker directory
    # This avoids file duplication and allows direct file access
    try:
        cmarker_dir = Path.home() / "AppData/Local/typst/packages/preview/cmarker/0.1.8"
        cmarker_images_dir = cmarker_dir / "images"

        # Remove existing symlink/directory if exists
        if cmarker_images_dir.exists():
            if cmarker_images_dir.is_symlink():
                cmarker_images_dir.unlink()
            else:
                shutil.rmtree(cmarker_images_dir)

        # Create symbolic link to our images directory
        cmarker_images_dir.symlink_to(images_dir.absolute())
        print(f"Created symbolic link: cmarker/images -> {images_dir.absolute()}")

    except Exception as e:
        print(f"Warning: Could not create symbolic link: {e}")
        print("Falling back to copying images...")
        # Fallback to copying if symlink fails
        try:
            cmarker_dir = (
                Path.home() / "AppData/Local/typst/packages/preview/cmarker/0.1.8"
            )
            cmarker_images_dir = cmarker_dir / "images"
            cmarker_images_dir.mkdir(parents=True, exist_ok=True)

            for image_path in images_dir.glob("*"):
                if image_path.suffix.lower() in [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".gif",
                    ".svg",
                    ".webp",
                ]:
                    dest_path = cmarker_images_dir / image_path.name
                    if not dest_path.exists():
                        shutil.copy2(image_path, dest_path)

            print(f"Copied images to cmarker directory")
        except Exception as copy_error:
            print(f"Error copying images: {copy_error}")

    font_str = ", ".join(f'"{f}"' for f in fonts)
    content = f"""#import "@preview/cmarker:0.1.8"

#set page(paper: "a4", margin: 2%, columns: 2)
#set text(font: ({font_str}), size: 8pt)
#set par(justify: true)

#show image: set align(center)
#set image(width: 100%)

#cmarker.render(read("../{md_processed_path.name}"))"""

    typ_path = typs_dir / f"{filename}.typ"
    typ_path.write_text(content, encoding="utf-8")
    print(f"Created: {typ_path}")

    return typ_path, md_processed_path


def cleanup_images_and_links(filename):
    """Clean up images directory and cmarker symlink after compilation"""
    images_dir = Path("images")

    # First, remove cmarker symlink
    try:
        cmarker_images_dir = (
            Path.home() / "AppData/Local/typst/packages/preview/cmarker/0.1.8/images"
        )
        if cmarker_images_dir.exists() and cmarker_images_dir.is_symlink():
            cmarker_images_dir.unlink()
            print(f"Cleaned up cmarker symlink")
    except Exception as e:
        print(f"Warning: Could not cleanup cmarker symlink: {e}")

    # Then remove local images directory
    if images_dir.exists():
        shutil.rmtree(images_dir)
        print(f"Cleaned up images directory: {images_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate Typst file from Markdown (2-column layout)"
    )
    parser.add_argument("filename", help="Markdown filename (without .md extension)")
    parser.add_argument(
        "--font",
        action="append",
        dest="fonts",
        help="Font name (can be specified multiple times)",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up processed markdown file after compilation",
    )
    parser.add_argument(
        "--cleanup-images",
        action="store_true",
        help="Clean up images directory and cmarker symlink after compilation",
    )
    args = parser.parse_args()

    fonts = args.fonts if args.fonts else ["MonaspiceNe NFM", "Sarasa Mono SC"]
    filename = args.filename
    typ_path, md_processed_path = generate_typ(filename, fonts)

    # Clean up processed markdown file if requested
    if args.cleanup:
        md_processed_path.unlink()
        print(f"Cleaned up: {md_processed_path}")

    # Clean up images and symlink if requested
    if args.cleanup_images:
        cleanup_images_and_links(filename)
