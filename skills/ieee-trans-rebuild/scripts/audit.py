#!/usr/bin/env python3
"""Audit every converted paper folder for acceptance criteria.

Checks per folder:
  1. manifest.json -> source PDF page count vs rebuilt main.pdf page count
  2. main.log: LaTeX errors, undefined references/citations, overfull hbox > 20pt
  3. main.tex \\includegraphics targets all resolve to files in figures/
  4. compare/report.md + compare_pNN.png present
  5. overleaf zip: contains main.tex, IEEEtran.cls, figures

Usage:
  audit.py [--root DIR] [--exempt FOLDER ...] [folder ...]

--root    workspace root holding the numbered converted folders
          (default: current directory)
--exempt  folder name(s) not required to match original page count
          (e.g. Elsevier pre-proof re-typeset in IEEE two-column)
folder    audit only these folders (default: all folders matching ^\\d{2}_)

Run with the research env:  ~/anaconda3/envs/research/bin/python -I audit.py --root <dir>
"""
import argparse
import glob
import json
import os
import re
import zipfile

import fitz

OVERFULL_LIMIT = 20.0  # pt


def check_folder(root, folder, exempt):
    d = os.path.join(root, folder)
    r = {"folder": folder, "issues": []}

    # ---- 1. page counts ----
    man = os.path.join(d, "manifest.json")
    orig_pages = None
    if os.path.exists(man):
        with open(man) as f:
            meta = json.load(f)
        src = meta.get("pdf", "")
        if src and os.path.exists(src):
            orig_pages = len(fitz.open(src))
    r["orig_pages"] = orig_pages

    pdf = os.path.join(d, "main.pdf")
    new_pages = len(fitz.open(pdf)) if os.path.exists(pdf) else None
    r["new_pages"] = new_pages
    if new_pages is None:
        r["issues"].append("main.pdf missing")
    elif orig_pages and folder not in exempt and new_pages != orig_pages:
        r["issues"].append(f"page mismatch {orig_pages}->{new_pages}")

    # unresolved "??" in rendered pdf text
    if new_pages:
        doc = fitz.open(pdf)
        qq = sum(page.get_text().count("??") for page in doc)
        if qq:
            r["issues"].append(f"'??' x{qq} in pdf text")
        doc.close()

    # ---- 2. compile log ----
    log = os.path.join(d, "main.log")
    r["errors"], r["undef"], r["overfull20"] = 0, 0, 0
    if os.path.exists(log):
        with open(log, encoding="utf8", errors="replace") as f:
            txt = f.read()
        r["errors"] = len(re.findall(r"^! ", txt, re.M))
        r["undef"] = len(re.findall(
            r"LaTeX Warning: (?:Reference|Citation).*undefined", txt))
        for m in re.finditer(r"Overfull \\hbox \((\d+(?:\.\d+)?)pt", txt):
            if float(m.group(1)) > OVERFULL_LIMIT:
                r["overfull20"] += 1
        if os.path.exists(pdf) and "Fatal error occurred" in txt and r["errors"] == 0:
            r["issues"].append("log fatal but no '!' captured")
    else:
        r["issues"].append("main.log missing")

    # ---- 3. includegraphics targets ----
    missing_gfx = []
    tex_files = glob.glob(os.path.join(d, "*.tex"))
    for tf in tex_files:
        with open(tf, encoding="utf8", errors="replace") as f:
            body = f.read()
        for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", body):
            target = m.group(1).strip()
            base = os.path.join(d, target)
            if not (os.path.exists(base)
                    or os.path.exists(base + ".pdf")
                    or os.path.exists(base + ".png")):
                missing_gfx.append(os.path.basename(tf) + ":" + target)
    r["gfx_missing"] = missing_gfx
    if missing_gfx:
        r["issues"].append(f"missing graphics x{len(missing_gfx)}")

    # ---- 4. compare outputs ----
    rep = os.path.join(d, "compare", "report.md")
    cmp_imgs = glob.glob(os.path.join(d, "compare", "compare_p*.png"))
    r["report"] = os.path.exists(rep)
    r["cmp_imgs"] = len(cmp_imgs)
    if not r["report"]:
        r["issues"].append("compare/report.md missing")
    if new_pages and r["cmp_imgs"] < new_pages:
        r["issues"].append(f"compare imgs {r['cmp_imgs']} < {new_pages}")

    # ---- 5. zip ----
    zips = glob.glob(os.path.join(d, "*.zip"))
    r["zip"] = os.path.basename(zips[0]) if zips else None
    if zips:
        with zipfile.ZipFile(zips[0]) as z:
            names = z.namelist()
            have_tex = any(n.endswith("main.tex") for n in names)
            have_cls = any(n.endswith("IEEEtran.cls") for n in names)
            nfig = sum(1 for n in names if n.startswith("figures/")
                       and n.endswith(".pdf"))
            r["zip_info"] = f"tex:{have_tex} cls:{have_cls} figs:{nfig}"
            if not have_tex:
                r["issues"].append("zip lacks main.tex")
            if not have_cls:
                r["issues"].append("zip lacks IEEEtran.cls")
            if nfig == 0:
                r["issues"].append("zip lacks figure pdfs")
    else:
        r["issues"].append("zip missing")

    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folders", nargs="*",
                    help="audit only these folders (default: all ^NN_ folders)")
    ap.add_argument("--root", default=os.getcwd(),
                    help="workspace root holding converted folders")
    ap.add_argument("--exempt", action="append", default=[],
                    help="folder exempt from page-count check (repeatable)")
    args = ap.parse_args()

    root = args.root
    folders = args.folders or sorted(
        x for x in os.listdir(root)
        if re.match(r"^\d{2}_", x) and os.path.isdir(os.path.join(root, x)))
    if not folders:
        raise SystemExit(f"no numbered folders found under {root}")

    rows, all_issues = [], []
    for folder in folders:
        r = check_folder(root, folder, set(args.exempt))
        all_issues.append(r)
        status = "OK" if not r["issues"] else "FAIL"
        rows.append(
            f"| {folder} | {r['orig_pages']} | {r['new_pages']} "
            f"| {r['errors']} | {r['undef']} | {r['overfull20']} "
            f"| {r['gfx_missing'] and len(r['gfx_missing']) or 0} "
            f"| {r['report']} | {r['cmp_imgs']} | {r['zip']} "
            f"| {r.get('zip_info','-')} | **{status}** |")
        for iss in r["issues"]:
            print(f"  [{folder}] ISSUE: {iss}")
            for g in r.get("gfx_missing", []):
                print(f"      -> {g}")

    print()
    print("| 文件夹 | 原页数 | 新页数 | 编译err | 未解析ref | overfull>20pt | 缺图 | report | 对比图 | zip | zip内容 | 状态 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for row in rows:
        print(row)
    nfail = sum(1 for r in all_issues if r["issues"])
    print(f"\nSUMMARY: {len(all_issues)} folders, {nfail} with issues")


if __name__ == "__main__":
    main()
