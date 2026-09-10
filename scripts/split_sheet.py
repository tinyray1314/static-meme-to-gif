#!/usr/bin/env python3
"""Split an inspected, uniform, gutter-free sprite sheet in row-major order."""
import argparse
import json
from pathlib import Path
from PIL import Image


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--image', type=Path, required=True)
    p.add_argument('--columns', type=int, required=True)
    p.add_argument('--rows', type=int, required=True)
    p.add_argument('--total-ms', type=int, default=2000)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    if a.columns < 1 or a.rows < 1:
        p.error('columns and rows must be positive')
    count = a.columns * a.rows
    if count < 2 or a.total_ms < count * 20 or a.total_ms % 10:
        p.error('Need >=2 cells and total-ms divisible by 10, allowing >=20ms per frame')
    if a.out.exists():
        p.error('Output directory exists; choose a new directory')
    with Image.open(a.image) as im:
        if im.width % a.columns or im.height % a.rows:
            p.error('Image dimensions are not divisible by the requested grid')
        width, height = im.width // a.columns, im.height // a.rows
        a.out.mkdir(parents=True)
        names = []
        for i in range(count):
            x, y = i % a.columns * width, i // a.columns * height
            name = f'{i + 1:02}.png'
            im.crop((x, y, x + width, y + height)).save(a.out / name)
            names.append(name)
    (a.out / 'manifest.json').write_text(json.dumps(
        dict(frames=names, total_ms=a.total_ms), indent=2) + '\n', encoding='utf-8')
    print(f'Split {count} frames ({width}x{height}); inspect cell boundaries before encoding.')


if __name__ == '__main__':
    main()
