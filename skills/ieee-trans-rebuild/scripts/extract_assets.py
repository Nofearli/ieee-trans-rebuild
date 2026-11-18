#!/usr/bin/env python3
"""Per-paper asset extraction for PDF -> LaTeX conversion.

Outputs (under <outdir>):
  pages/page_NN.png     180dpi page renders (for agent reading)
  text/page_NN.txt      per-page text layer (content-stream order, IEEE-friendly)
  figures/figNNN_pNN.pdf  vector crop of each detected figure/table region
  figures/figNNN_pNN.png  400dpi raster preview of the same region
  manifest.json         region inventory with page, bbox, caption hint, text density

Usage: extract_assets.py <pdf> <outdir> [page_dpi]
"""
import json
import os
import sys

import fitz  # PyMuPDF


def merge_boxes(boxes, gap=8.0, rounds=6):
    """Merge rects that overlap or nearly touch (expanded by gap/2)."""
    boxes = [fitz.Rect(b) for b in boxes]
    for _ in range(rounds):
        changed = False
        out = []
        while boxes:
            cur = fitz.Rect(boxes.pop(0))
            grown = fitz.Rect(cur.x0 - gap / 2, cur.y0 - gap / 2,
                              cur.x1 + gap / 2, cur.y1 + gap / 2)
            keep = []
            for b in boxes:
                if grown.intersects(b):
                    cur |= b
                    changed = True
                else:
                    keep.append(b)
            boxes = keep
            out.append(cur)
        boxes = out
        if not changed:
            break
    return boxes


def chars_in_box(page, box):
    """Number of text characters whose block center falls inside box."""
    n = 0
    for x0, y0, x1, y1, txt, *_ in page.get_text("blocks"):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        if box.x0 <= cx <= box.x1 and box.y0 <= cy <= box.y1:
            n += len(txt.strip())
    return n


def caption_hint(page, box):
    """First 70 chars of a nearby 'Fig.'/'TABLE' caption block, if any."""
    best = None
    for x0, y0, x1, y1, txt, *_ in page.get_text("blocks"):
        t = txt.strip().replace("\n", " ")
        low = t.lower()
        if not (low.startswith("fig.") or low.startswith("figure")
                or low.startswith("table")):
            continue
        overlap = min(box.x1, x1) - max(box.x0, x0)
        if overlap <= 0:
            continue
        vdist = max(box.y0 - y1, y0 - box.y1)
        if 0 <= vdist < 60:
            if best is None or vdist < best[0]:
                best = (vdist, t[:70])
    return best[1] if best else ""


def main(pdf_path, outdir, page_dpi=180):
    doc = fitz.open(pdf_path)
    pages_dir = os.path.join(outdir, "pages")
    text_dir = os.path.join(outdir, "text")
    figs_dir = os.path.join(outdir, "figures")
    for d in (pages_dir, text_dir, figs_dir):
        os.makedirs(d, exist_ok=True)

    manifest = []
    fig_idx = 0
    for pno, page in enumerate(doc):
        n = pno + 1
        page.get_pixmap(dpi=page_dpi).save(
            os.path.join(pages_dir, f"page_{n:02d}.png"))
        with open(os.path.join(text_dir, f"page_{n:02d}.txt"), "w") as f:
            f.write(page.get_text("text"))

        W, H = page.rect.width, page.rect.height
        area = W * H
        raw = []
        for info in page.get_image_info():
            r = fitz.Rect(info["bbox"])
            if r.get_area() > 0.0008 * area and r.width > 15 and r.height > 15:
                raw.append(r)
        try:
            clusters = page.cluster_drawings()
        except Exception:
            clusters = []
        for r in clusters:
            r = fitz.Rect(r)
            if (r.get_area() > 0.0008 * area and r.width > 20
                    and r.height > 20 and r.get_area() < 0.9 * area):
                raw.append(r)

        for box in merge_boxes(raw):
            box = fitz.Rect(box) & page.rect
            if box.is_empty or box.get_area() < 0.0008 * area:
                continue
            if box.get_area() > 0.97 * area:  # full-page background
                continue
            fig_idx += 1
            fid = f"fig{fig_idx:03d}_p{n:02d}"
            # vector crop (keeps strokes/text sharp)
            vdoc = fitz.open()
            vpage = vdoc.new_page(width=box.width, height=box.height)
            vpage.show_pdf_page(vpage.rect, doc, pno, clip=box)
            vdoc.save(os.path.join(figs_dir, fid + ".pdf"))
            vdoc.close()
            # 400dpi raster preview
            page.get_pixmap(dpi=400, clip=box).save(
                os.path.join(figs_dir, fid + ".png"))
            manifest.append({
                "id": fid,
                "page": n,
                "bbox": [round(v, 1) for v in box],
                "width_pt": round(box.width, 1),
                "height_pt": round(box.height, 1),
                "spans_columns": box.width > W * 0.62,
                "chars_inside": chars_in_box(page, box),
                "caption_hint": caption_hint(page, box),
                "pdf": f"figures/{fid}.pdf",
                "png": f"figures/{fid}.png",
            })

    with open(os.path.join(outdir, "manifest.json"), "w") as f:
        json.dump({"pdf": pdf_path, "pages": len(doc),
                   "regions": manifest}, f, ensure_ascii=False, indent=1)
    print(f"pages={len(doc)} regions={len(manifest)} -> {outdir}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         int(sys.argv[3]) if len(sys.argv) > 3 else 180)
