#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageOps


def to_rgb(image: Image.Image) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    if image.mode in {"RGBA", "LA"} or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "#FFFFFF")
        background.paste(rgba, mask=rgba.getchannel("A"))
        return background
    return image.convert("RGB")


def resize_to_max_width(image: Image.Image, max_width: int) -> Image.Image:
    if image.width <= max_width:
        return image
    height = round(image.height * max_width / image.width)
    return image.resize((max_width, height), Image.Resampling.LANCZOS)


def save_under_limit(
    image: Image.Image,
    output: Path,
    max_bytes: int,
    initial_quality: int,
) -> tuple[Image.Image, int]:
    quality = initial_quality
    current = image

    while True:
        current.save(output, "JPEG", quality=quality, optimize=True, progressive=True)
        if output.stat().st_size <= max_bytes:
            return current, quality

        quality -= 5
        if quality >= 55:
            continue

        next_width = round(current.width * 0.9)
        if next_width < 400:
            raise SystemExit(f"Não foi possível reduzir a capa para {max_bytes} bytes.")
        next_height = round(current.height * next_width / current.width)
        current = current.resize((next_width, next_height), Image.Resampling.LANCZOS)
        quality = initial_quality


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepara uma capa para upload no Sharebook.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-bytes", type=int, default=800_000)
    parser.add_argument("--max-width", type=int, default=1200)
    parser.add_argument("--quality", type=int, default=90)
    args = parser.parse_args()

    if not args.input.is_file():
        raise SystemExit(f"Arquivo de entrada não encontrado: {args.input}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(args.input) as source:
        prepared = resize_to_max_width(to_rgb(source), args.max_width)
        final, quality = save_under_limit(
            prepared,
            args.output,
            args.max_bytes,
            args.quality,
        )

    print(
        json.dumps(
            {
                "output": str(args.output.resolve()),
                "width": final.width,
                "height": final.height,
                "bytes": args.output.stat().st_size,
                "quality": quality,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
