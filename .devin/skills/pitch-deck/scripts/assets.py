"""Copy captured screens into docs/04-pitch/assets under the names the deck uses.

Usage: python assets.py <shots_dir> [repo_root]
CROP trims empty white space on the right of wide cards so their text stays readable on a slide.
"""
import os, sys
from PIL import Image

NAMES = {  # capture name -> asset name used in presentation.html
    "p-need": "need", "p-aino-card": "aino-card", "p-choose": "choose", "p-choices": "choices",
    "p-talks": "talks", "p-map": "map", "p-record": "record", "p-fair": "fair", "p-chase": "chase",
    "p-report": "report", "m-day": "phone-day", "m-pass": "phone-pass", "m-after": "phone-after",
    "d-online": "online",
}
CROP = {"p-need": 1440, "p-aino-card": 1620}  # keep this many px from the left


def main(shots, root="."):
    out = os.path.join(root, "docs", "04-pitch", "assets")
    os.makedirs(out, exist_ok=True)
    for src, dst in NAMES.items():
        path = os.path.join(shots, src + ".png")
        if not os.path.exists(path):
            print("missing", src); continue
        im = Image.open(path).convert("RGB")
        if src in CROP:
            im = im.crop((0, 0, min(CROP[src], im.width), im.height))
        im.save(os.path.join(out, dst + ".png"), optimize=True)
        print(dst, im.size)


if __name__ == "__main__":
    main(*sys.argv[1:])
