# 04 · 图表提取规则

**原则：图从原 PDF 矢量裁剪（保清晰度），400dpi png 兜底；表用 booktabs 重排而非截图。**

## 1. 自动提取（extract_assets.py）

- 输出 `figures/figNNN_pNN.{pdf,png}` + `manifest.json`（bbox、caption 提示、`spans_columns`、chars_inside）。
- 检测 = 位图 bbox（`get_image_info`）+ 矢量簇（`cluster_drawings`）合并（gap 8pt×6 轮）。
- 已知局限：
  - 单栏 Elsevier 版式下候选多为正文块（实测 11 号篇自动检测基本失效）；
  - 相邻图会被合并；跨栏图可能被切成两半；无框纯表格检测不到。

## 2. 手工修正（自动结果不对时）

在工程里写 `make_crops.py`（矢量裁剪 API 同 extract_assets：`show_pdf_page` + clip），bbox 从原版量：

```python
import fitz
CROPS = [  # (page1based, (x0,y0,x1,y1)pt, name)
    (2, (130.1, 139.1, 424.4, 354.7), "fig1"),
    (9, (60, 60, 300, 300), "bio1"),          # 作者照片
]
doc = fitz.open(SRC)
for p, box, name in CROPS:
    v = fitz.open(); pg = v.new_page(width=box[2]-box[0], height=box[3]-box[1])
    pg.show_pdf_page(pg.rect, doc, p-1, clip=fitz.Rect(*box))
    v.save(f"figures/{name}.pdf")
```

- bbox 量法：zoom.py 放大该页 → 目测边缘 → fitz `page.get_text("dict")`/`get_drawings()` 精确定位；裁完用 zoom.py 复核边缘是否切字。
- **sanity check**：对每张裁剪打印框内文字词（`page.get_text("words")` 与 bbox 相交），确认没把正文段落裁进图里。
- 命名：手工裁剪用语义名 `fig1_launch`、`bio1`；bbox 存 `figures/crops.json` 备查。
- 作者照片（IEEEbiography）：独立小裁剪 `bioN.pdf`，`[width=1in,height=1.25in,clip,keepaspectratio]` 引用。

## 3. 水印/ stamp 处理

- Elsevier pre-proof 的 "Journal Pre-proof" 水印是嵌入 Form XObject：**复制一份工作副本**，在工作副本上 blank/移除该 XObject 后再裁剪；**原始 PDF 永不修改**。
- IEEE 早期访问的 Xplore 页脚水印在页面文字层里：裁剪 bbox 避开页脚即可。

## 4. 表格

- 简单表：booktabs 重排（`\toprule/\midrule/\bottomrule`），数据从 text 层 + zoom 裁剪核对。
- 复杂表（合并单元格、斜线表头）：`array/multirow` 复刻；实在无法重排的才走矢量裁剪 + `table*` 包图，并在 report.md 注明。
- 裁剪表图注意 `spans_columns`：跨栏表必须 `table*`，否则会压进单栏溢出。

## 5. 正文引用

- `\includegraphics` 不带扩展名（audit 按 `.pdf`/`.png` 兜底解析）。
- 同名多格式共存时 pdf 优先（矢量清晰）。
- caption 逐字照抄原版（含 subfig 的 (a)(b) 标注文字）。
