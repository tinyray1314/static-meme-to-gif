#!/usr/bin/env python3
"""Deterministic GIF assembly and size-budget compression. Requires Pillow."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageOps, ImageColor, ImageSequence


def inspect(path):
    with Image.open(path) as im:
        durations = [f.info.get('duration', 0) for f in ImageSequence.Iterator(im)]
        return dict(size=list(im.size), frames=len(durations), durations_ms=durations,
                    total_ms=sum(durations), loop=im.info.get('loop'), bytes=path.stat().st_size)


def encode(frames, durations, path, colors):
    # One palette sampled across the whole sequence prevents palette flicker.
    atlas = Image.new('RGB', (128 * len(frames), 128))
    for i, frame in enumerate(frames):
        atlas.paste(ImageOps.pad(frame, (128, 128)), (128 * i, 0))
    palette = atlas.quantize(colors=colors)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=durations,
                    loop=0, disposal=2, optimize=False)
    result = inspect(path)
    if result['total_ms'] != sum(durations) or result['loop'] != 0:
        raise ValueError('Encoded timing or loop differs from requested output')
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--manifest', type=Path)
    source.add_argument('--gif', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--size', type=int, default=240)
    p.add_argument('--max-kb', type=float, default=500)
    p.add_argument('--background', default='#FFFFFF')
    a = p.parse_args()
    if a.size < 1 or a.max_kb <= 0:
        p.error('size and max-kb must be positive')
    bg = ImageColor.getrgb(a.background)
    if len(bg) != 3:
        p.error('background must be an opaque RGB color')
    if a.manifest:
        data = json.loads(a.manifest.read_text())
        frames = []
        for name in data['frames']:
            with Image.open(a.manifest.parent / name) as im:
                frames.append(im.convert('RGBA'))
        n = len(frames)
        total = data.get('total_ms', 2000)
        if not isinstance(total, int) or total % 10 or total < n * 20:
            p.error('total_ms must be a multiple of 10 and allow >=20ms per frame')
        ticks, remainder = divmod(total // 10, n) if n else (0, 0)
        durations = data.get('durations_ms', [10 * (ticks + (i < remainder)) for i in range(n)])
        if sum(durations) != total:
            p.error('durations_ms must sum to total_ms')
    else:
        with Image.open(a.gif) as im:
            frames, durations = [], []
            for f in ImageSequence.Iterator(im):
                frames.append(f.convert('RGBA'))
                durations.append(f.info.get('duration', 100))
    if len(frames) < 2 or len(durations) != len(frames):
        p.error('Need >=2 frames and one duration per frame')
    if any(not isinstance(d, int) or d < 20 or d % 10 for d in durations):
        p.error('Frame durations must be integer multiples of 10ms, at least 20ms')
    if len({f.size for f in frames}) != 1:
        p.error('Frame sizes differ; inspect and normalize composition before encoding')
    flattened = []
    for f in frames:
        canvas = Image.new('RGBA', f.size, bg + (255,))
        flattened.append(Image.alpha_composite(canvas, f).convert('RGB'))
    a.out.mkdir(parents=True, exist_ok=True)
    paths = [a.out / name for name in ('master.gif', 'small.gif', 'report.json')]
    if any(path.exists() for path in paths):
        p.error('Output exists; choose a new output directory')
    master = encode(flattened, durations, paths[0], 256)
    small_frames = [ImageOps.pad(f, (a.size, a.size), method=Image.Resampling.LANCZOS,
                                color=bg) for f in flattened]
    attempts = []
    for colors in (256, 128, 64):
        small = encode(small_frames, durations, paths[1], colors)
        attempts.append(dict(colors=colors, bytes=small['bytes']))
        if small['bytes'] <= a.max_kb * 1024:
            break
    report = dict(input_frames=len(frames), master=master, small=small,
                  palette_attempts=attempts, budget_bytes=a.max_kb * 1024,
                  budget_met=small['bytes'] <= a.max_kb * 1024,
                  background=a.background, visual_check='NOT RUN', platform_import='NOT RUN')
    paths[2].write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
