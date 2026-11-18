#!/usr/bin/env python
"""Slice a long screenshot (WeChat chat export) into A4-ratio pages.

Strategy: detect horizontal all-blank bands (whitespace gaps) and cut at the
gap nearest to the target page height, so no text/figure is sliced through.
Falls back to a hard cut at the target height if no gap exists in the window.

Outputs (under <outdir>):
  pages/page_NN.png        slices, RGB
  original_from_png.pdf    slices composed as PDF pages (pt = px / scale)
  manifest.json            {"pdf": <pdf path>, "pages": N, "regions": [], "source_png": ...}

Usage: slice_longscreenshot.py <long.png> <outdir> [--scale 2.0] [--target-px 1600]
scale = screenshot px per PDF pt (1189px / 595pt ~ 2.0 for a 2x A4 screenshot).
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

import fitz  # PyMuPDF


def blank_runs(row_darkness):
    """Yield (start, end) of consecutive blank (no content) row runs."""
    runs, start = [], None
    for i, dark in enumerate(row_darkness):
        if dark:
            if start is not None:
                runs.append((start, i))
                start = None
        else:
            if start is None:
                start = i
    if start is not None:
        runs.append((start, len(row_darkness)))
    return runs


def slice_points(H, row_darkness, target, window=0.15):
    """Choose cut rows near multiples of target, preferring real gaps."""
    cuts, pos = [], 0
    while H - pos > target * (1 + window):
        ideal = pos + target
        lo, hi = int(ideal * (1 - window)), int(ideal * (1 + window))
        candidates = [c for c in cuts_from_gaps(blank_runs(row_darkness), lo, hi)]
        cut = min(candidates, key=lambda c: abs(c - ideal)) if candidates \
            else min(ideal, H - 1)
        cuts.append(int(cut))
        pos = cuts[-1]
    return cuts


def cuts_from_gaps(runs, lo, hi):
    for a, b in runs:
        if b - a < 30:            # too thin to be a real gap
            continue
        mid = (a + b) // 2
        if lo <= mid <= hi:
            yield mid


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("png")
    ap.add_argument("outdir")
    ap.add_argument("--scale", type=float, default=2.0,
                    help="screenshot px per PDF pt")
    ap.add_argument("--target-px", type=int, default=1600,
                    help="target slice height in px")
    args = ap.parse_args()

    os.makedirs(os.path.join(args.outdir, "pages"), exist_ok=True)
    im = Image.open(args.png)
    if im.mode != "RGB":
        im = im.convert("RGB")
    W, H = im.size
    arr = np.asarray(im)
    # a row has content if any pixel is darker than 235 on any channel
    row_darkness = (arr.min(axis=2) < 235).any(axis=1)

    cuts = slice_points(H, row_darkness, args.target_px)
    bounds = [0] + cuts + [H]

    pdf = fitz.open()
    import io
    for i in range(len(bounds) - 1):
        top, bot = bounds[i], bounds[i + 1]
        crop = im.crop((0, top, W, bot))
        name = os.path.join(args.outdir, "pages", f"page_{i + 1:02d}.png")
        crop.save(name)
        buf = io.BytesIO()
        crop.save(buf, format="PNG")
        pt_w, pt_h = W / args.scale, (bot - top) / args.scale
        page = pdf.new_page(width=pt_w, height=pt_h)
        page.insert_image(fitz.Rect(0, 0, pt_w, pt_h), stream=buf.getvalue())
    pdf_path = os.path.join(args.outdir, "original_from_png.pdf")
    pdf.save(pdf_path)
    pdf.close()

    manifest = {"pdf": pdf_path, "pages": len(bounds) - 1, "regions": [],
                "source_png": args.png}
    with open(os.path.join(args.outdir, "manifest.json"), "w") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"slices={len(bounds) - 1} -> {args.outdir}")


if __name__ == "__main__":
    main()
