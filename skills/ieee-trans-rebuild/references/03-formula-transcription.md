# 03 · 公式转录规则（质量核心）

**原则：公式全部手写 LaTeX，逐条对照高倍位图核验。任何自动来源（PDF 文字层、mineru）都只作草稿，不直接采信。**

## 1. 为什么不能抄文字层 / 不能直接用 mineru 输出

- PDF 文字层**系统性丢失希腊字母、上下标层级、特殊数学符号**（实测多篇 `\alpha` 变 `a`、`x^T` 变 `xT`、范数/期望符号直接消失）。
- mineru 的公式 OCR 质量好但同样会错：嵌套上下标、`d` 正斜体区分、多行对齐公式的 `&` 位置、矩阵省略号——不核验就会错进论文。

## 2. 工作法

1. 对公式密集页生成 zoom 裁剪（zoom 3.0 起步；下标争议、间距争议拉到 6–10 倍）：

```bash
~/anaconda3/envs/research/bin/python -I ~/.zcode/skills/ieee-trans-rebuild/scripts/zoom.py \
    <源.pdf> --outdir <工程>/zoom --json clips.json
```

clips.json 示例（按公式块分条，命名可读）：

```json
[{"page": 3, "bbox": [40, 380, 316, 770], "zoom": 3.0, "name": "p3_left_eq1"},
 {"page": 5, "bbox": [300, 300, 570, 620], "zoom": 5.0, "name": "p5_right_eq17_where"}]
```

快速起手可用整栏模式：`--page 3 --column left`（left/right/full 预设栏框）。

2. 对照裁剪**手写**每条公式；multi-line 公式用 `align`/`split` 还原原版换行与对齐点。
3. 写完一节，再**逐条回看**：渲染出的 main.pdf 公式 vs zoom 裁剪并排比对（编号、标点、where 从句位置都要对上）。
4. 公式编号与原版一一对应；原版不编号的 display 公式保持不编号。

## 3. 高频错误清单（核验时重点盯）

- 希腊字母大小写（`\alpha/\Alpha` 型混淆）；`\mathrm{d}` vs 斜体 d
- 上标转置 `^\top` / `^\mathrm{T}` 与原版一致；范数 `\|\cdot\|` 层数
- 期望/方差算子正体 `\mathbb{E}`；diag/log/exp 正体 `\mathrm{diag}` 或 `\operatorname{diag}`
- 多行公式在原版的断行点与对齐字符（`&=` 对齐在哪一列）
- where 从句：原版跟在公式尾部换行的，`&\quad \text{where ...}` 复刻
- 分式嵌套的紧凑 vs 全尺寸（落位需要时可 `\frac` → `\tfrac`，记入遗留差异）

## 4. 记录

compare/report.md 的"公式"栏写明：全部手写 + zoom 核验 + 有争议条的 zoom 文件名，便于复查。
