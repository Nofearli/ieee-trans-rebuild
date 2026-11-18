#!/usr/bin/env python
"""Render zoomed clips of a PDF for careful equation / small-detail transcription.

Two modes:

1. Single clip:
   zoom.py <pdf> --page N --bbox x0,y0,x1,y1 [--zoom Z] [--out NAME.png]
   (--column left|right|full may replace --bbox on a two-column page)

2. Batch clips from a JSON file:
   zoom.py <pdf> --json clips.json --outdir DIR
   clips.json entries: {"page": 3, "bbox": [x0,y0,x1,y1], "zoom": 3.0,
                        "name": "p3_left_eq1"}
   ("bbox" may be omitted when "column" is "left"/"right"/"full".

Coordinates are PDF points, origin at page top-left, y downward.
Default zoom 3.0 (~216 dpi); push to 6-10 for subscript/spacing disputes.

Output default dir: <pdf-dir>/zoom/
"""
import argparse
import json
import os

import fitz  # PyMuPDF

DEFAULT_ZOOM = 3.0


def column_bbox(page, which):
    """Convenience boxes for a two-column IEEE-style page (pt).

    Derived from the page width so it adapts to letter/A4; the classic
    letter geometry is left 40-316, right 300-570 with a small overlap
    so nothing at the column edge is cut off.
    """
    W, H = page.rect.width, page.rect.height
    mid = W / 2
    if which == "left":
        return fitz.Rect(36, 30, mid + 18, H - 30)
    if which == "right":
        return fitz.Rect(mid - 18, 30, W - 36, H - 30)
    return fitz.Rect(36, 30, W - 36, H - 30)


def render(doc, page_no, bbox, zoom, out_path):
    page = doc[page_no - 1]  # 1-based page number in, 0-based index
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom),
                          clip=fitz.Rect(*bbox), alpha=False)
    pix.save(out_path)
    print(out_path, pix.width, pix.height)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pdf")
    ap.add_argument("--json", help="batch clips file")
    ap.add_argument("--outdir", help="output directory (default <pdf-dir>/zoom)")
    ap.add_argument("--page", type=int, help="1-based page number (single mode)")
    ap.add_argument("--bbox", help="x0,y0,x1,y1 in pt (single mode)")
    ap.add_argument("--column", choices=["left", "right", "full"],
                    help="preset column bbox instead of --bbox")
    ap.add_argument("--zoom", type=float, default=DEFAULT_ZOOM)
    ap.add_argument("--out", help="output png name (single mode)")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    outdir = args.outdir or os.path.join(os.path.dirname(os.path.abspath(args.pdf)),
                                         "zoom")
    os.makedirs(outdir, exist_ok=True)

    if args.json:
        with open(args.json, encoding="utf8") as f:
            clips = json.load(f)
        for c in clips:
            page_no = c["page"]
            bbox = c.get("bbox") or column_bbox(doc[page_no - 1],
                                                c.get("column", "full"))
            zoom = c.get("zoom", DEFAULT_ZOOM)
            name = c.get("name", f"p{page_no}_clip")
            render(doc, page_no, bbox, zoom,
                   os.path.join(outdir, name + ".png"))
    else:
        if not args.page or not (args.bbox or args.column):
            ap.error("single mode needs --page and (--bbox or --column)")
        page = doc[args.page - 1]
        bbox = (list(map(float, args.bbox.split(","))) if args.bbox
                else column_bbox(page, args.column))
        name = (args.out or f"p{args.page}_clip").removesuffix(".png")
        render(doc, args.page, bbox, args.zoom,
               os.path.join(outdir, name + ".png"))


if __name__ == "__main__":
    main()
