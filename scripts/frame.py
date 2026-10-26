"""Crop every render in build/ to its content and centre it on an identical 16:10 white
canvas, so a series of very different proteins reads as one set.

    python scripts/frame.py            # build/*.png -> figures/*.webp
    python scripts/frame.py --fill 0.8 # how much of the canvas the molecule may fill
"""
import argparse
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent.parent


def frame(src: Path, dst: Path, fill: float, size=(1600, 1000)) -> None:
    w, h = size
    im = Image.open(src).convert('RGB')
    box = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).getbbox()
    im = im.crop(box)
    k = min(w * fill / im.width, h * fill / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    canvas = Image.new('RGB', size, 'white')
    canvas.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    canvas.save(dst, 'WEBP', quality=86, method=6)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fill', type=float, default=0.8)
    args = ap.parse_args()
    out = ROOT / 'figures'
    out.mkdir(exist_ok=True)
    for png in sorted((ROOT / 'build').glob('*.png')):
        frame(png, out / f'{png.stem}.webp', args.fill)
        print(f'{png.name} -> figures/{png.stem}.webp')


if __name__ == '__main__':
    main()
