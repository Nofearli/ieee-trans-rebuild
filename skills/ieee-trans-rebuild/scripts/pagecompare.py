#!/usr/bin/env python3
"""Side-by-side page comparison: original PDF (left) vs rebuilt PDF (right).

Outputs <outdir>/compare_pNN.png plus a page-count line on stdout.

Usage: pagecompare.py <original.pdf> <rebuilt.pdf> <outdir> [dpi]
"""
import os
import sys

import fitz
from PIL import Image, ImageDraw


def main(orig, new, outdir, dpi=100):
    os.makedirs(outdir, exist_ok=True)
    d1, d2 = fitz.open(orig), fitz.open(new)
    n = max(len(d1), len(d2))
    for i in range(n):
        imgs = []
        for label, d in (("ORIGINAL", d1), ("REBUILT", d2)):
            if i < len(d):
                tmp = os.path.join(outdir, f"_tmp_{label}.png")
                d[i].get_pixmap(dpi=dpi).save(tmp)
                imgs.append((label, Image.open(tmp)))
            else:
                imgs.append((label, Image.new("RGB", (300, 400), "#dddddd")))
        w = sum(im.width for _, im in imgs) + 30
        h = max(im.height for _, im in imgs) + 46
        canvas = Image.new("RGB", (w, h), "white")
        draw = ImageDraw.Draw(canvas)
        x = 10
        for label, im in imgs:
            draw.text((x + 2, 6), f"{label}  p.{i + 1}", fill="black")
            canvas.paste(im, (x, 30))
            x += im.width + 10
        canvas.save(os.path.join(outdir, f"compare_p{i + 1:02d}.png"))
    for _, im in imgs:
        im.close()
    print(f"orig_pages={len(d1)} rebuilt_pages={len(d2)} "
          f"diff={len(d2) - len(d1):+d} -> {outdir}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3],
         int(sys.argv[4]) if len(sys.argv) > 4 else 100)
