#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Generate or edit images using Gemini image models.

Usage:
    uv run generate_image.py --prompt "description" --filename "output.png"
"""

import argparse
import os
import sys
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image as PILImage

MODEL_ID = "gemini-3.1-flash-image"


def _log(msg: str) -> None:
    """Print status messages to stderr so stdout stays clean for machine parsing."""
    print(msg, file=sys.stderr)


def _get_api_key() -> str | None:
    """Get the API key from the portable environment contract."""
    return os.environ.get("GEMINI_API_KEY")


def _detect_resolution(image: PILImage.Image) -> str:
    """Auto-detect appropriate resolution from input image dimensions."""
    max_dim = max(image.size)
    if max_dim >= 3000:
        return "4K"
    elif max_dim >= 1500:
        return "2K"
    return "1K"


def _save_prompt_file(output_path: Path, prompt: str, resolution: str, input_image: str | None, model: str) -> Path:
    """Save a .prompt.md file alongside the generated image for iteration."""
    prompt_path = output_path.with_suffix(".prompt.md")
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    lines = [
        "---",
        f"model: {model}",
        f"resolution: {resolution}",
        f"timestamp: {timestamp}",
    ]
    if input_image:
        lines.append(f"input_image: {input_image}")
    lines += [
        f"output: {output_path.name}",
        "---",
        "",
        prompt,
        "",
    ]

    prompt_path.write_text("\n".join(lines))
    return prompt_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate or edit images using Nano Banana 2"
    )
    parser.add_argument("--prompt", "-p", required=True, help="Image description or editing instructions")
    parser.add_argument("--output", "--filename", "-f", dest="output", required=True, help="Output PNG path")
    parser.add_argument("--input-image", "-i", help="Input image path for editing/modification")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="1K",
                        help="Output resolution: 1K (default), 2K, or 4K")
    parser.add_argument("--model", default=MODEL_ID, help="Gemini image model identifier")

    args = parser.parse_args()

    api_key = _get_api_key()
    if not api_key:
        _log("Error: No API key found.")
        _log("Set GEMINI_API_KEY in the environment.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load input image if editing
    input_image = None
    resolution = args.resolution
    if args.input_image:
        try:
            input_image = PILImage.open(args.input_image)
            _log(f"Loaded input image: {args.input_image}")
            if args.resolution == "1K":  # default — auto-detect from input
                resolution = _detect_resolution(input_image)
                _log(f"Auto-detected resolution: {resolution} (from {input_image.size[0]}x{input_image.size[1]})")
        except Exception as e:
            _log(f"Error loading input image: {e}")
            sys.exit(1)

    # Build request
    if input_image:
        contents = [input_image, args.prompt]
        _log(f"Editing image with {args.model} at {resolution}...")
    else:
        contents = args.prompt
        _log(f"Generating image with {args.model} at {resolution}...")

    try:
        response = client.models.generate_content(
            model=args.model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
                image_config=types.ImageConfig(image_size=resolution),
            ),
        )

        image_saved = False
        for part in response.parts:
            if part.text is not None:
                _log(f"Model response: {part.text}")
            elif part.inline_data is not None:
                image = PILImage.open(BytesIO(part.inline_data.data))
                image.save(str(output_path), "PNG")
                image_saved = True

        if not image_saved:
            _log("Error: No image was generated in the response.")
            sys.exit(1)

        # Save prompt file for iteration
        prompt_path = _save_prompt_file(output_path, args.prompt, resolution, args.input_image, args.model)
        _log(f"Prompt saved: {prompt_path.resolve()}")

        # stdout: only the image path for easy parsing
        full_path = output_path.resolve()
        print(full_path)

    except Exception as e:
        _log(f"Error generating image ({args.model}, {resolution}): {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
