# 01 · 端到端工作流（单篇论文 → 完整 LaTeX 工程）

输入：一篇论文 PDF（通常 IEEE 两栏期刊稿；非 IEEE 稿的处理见下）。
输出：`converted/<NN>_<短名>/` 下的完整工程 + 逐页对比 + Overleaf zip。

**输入形态分支**：
- IEEE 会议稿（如 IECON）：用户可能要求统一 journal 版式重排（先问清）——重排时会议平台元素（版权侧栏）不复刻，页数豁免，内容完整为准。
- Elsevier 等非 IEEE 稿：IEEEtran 重排、页数豁免（见 references/02 与 06）。
- **长截图（PNG）等非 PDF 输入**：走 references/07-long-screenshot.md 的切页管线，中文文档用 ctexart+xelatex（audit 按魔法注释自动兼容）。
- 重复审稿副本：跳过，在 REPORT.md 注明。

## 阶段 0 · 预检与环境

```bash
which pdflatex                                    # texlive-base
kpsewhich IEEEtran.cls                            # texlive-publishers；没有也能跑，cls 已内置于 skill assets/
~/anaconda3/envs/research/bin/python -c "import fitz, PIL; print('ok')"   # PyMuPDF + Pillow
```

- 所有 Python 脚本一律 `~/anaconda3/envs/research/bin/python -I <skill>/scripts/xxx.py`。
- 建工作区：`<工作区>/converted/<NN>_<短名>/`；NN 续接该工作区现有最大编号（01、02…）；短名 = `年份_期刊缩写_主题关键词`（如 `04_tcst2026_defense_partial_info`）。
- 复制 cls：`cp ~/.zcode/skills/ieee-trans-rebuild/assets/IEEEtran.cls <工程>/`（工程自带 cls，Overleaf/换机都能编译）。

## 阶段 1 · 元数据核实（先于一切命名）

从 PDF 首页提取标题/作者/年份 → 按 `references/05-metadata-and-skills.md` 的核实链查证。
查不到的字段：文件名标"年份待核实/作者待核实"，工程内留 `% TODO` 注释记录已查渠道；**绝不编造**。

## 阶段 2 · 资产提取

```bash
~/anaconda3/envs/research/bin/python -I ~/.zcode/skills/ieee-trans-rebuild/scripts/extract_assets.py \
    <源.pdf> <工程>/ 180
```

产出（manifest.json 记录全部）：
- `pages/page_NN.png` — 180dpi 整页渲染（转录时逐页精读）
- `text/page_NN.txt` — 逐页文字层（注意：**文字层常丢希腊字母/数学符号，只当代码辅助，不当代码来源**）
- `figures/figNNN_pNN.{pdf,png}` — 自动检测的图表区域（矢量裁剪 + 400dpi 兜底）
- `manifest.json` — bbox、caption 提示、`spans_columns`（宽 > 0.62×页宽 → 正文里用 `figure*`）

自动检测不完美是常态：错误/漏检的图按 `references/04` 手工修 bbox 重裁。

## 阶段 3 · mineru 预解析（底稿，不直接采信）

调 mineru skill 对源 PDF 出 Markdown + LaTeX 公式草稿（PDF 会上传到 MinerU 云端，敏感稿勿用）。
用途：段落结构、参照文献列表、公式的**起点草稿**。
限制：mineru 与文字层同样会丢/错希腊字母、上下标、多层嵌套——**每个公式仍须按阶段 4 对照高倍裁剪核验**，底稿只省打字，不省校对。

## 阶段 4 · 逐节转录（质量核心）

1. **通读**：逐页读 `pages/page_NN.png` + `text/page_NN.txt`，对照 manifest 的 caption 提示。
2. **分节拆文件**：`sec_intro.tex`、`sec_problem.tex`… 按原版节结构；公式密集页先用 zoom.py 拉高倍裁剪：
   ```bash
   ~/anaconda3/envs/research/bin/python -I ~/.zcode/skills/ieee-trans-rebuild/scripts/zoom.py \
       <源.pdf> --outdir <工程>/zoom --json clips.json     # 或 --page 3 --column left --zoom 3
   ```
3. **公式全部手写 LaTeX**，逐条对照 zoom 裁剪核验（规则见 `references/03`）。
4. **文字逐字照抄**：摘要、caption、脚注、致谢、文献列表（`thebibliography` 编号与原版一一对应）；原版 typo 保留不修（忠实复刻）。
5. **结构复刻**：定理环境、伪代码框（ruled minipage）、图表编号与落位（见 `references/02`）。
6. 版面特殊元素（早期访问横幅/水印/版权块）按 `references/02` 第 4 节复刻。

> 转录可以派子代理并行分节；子代理多次被内容安全过滤器中断时（军事/博弈类论文常见），由主代理直接续写兜底，不要反复重试子代理。

## 阶段 5 · 编译与逐页对齐

```bash
cd <工程> && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex
~/anaconda3/envs/research/bin/python -I ~/.zcode/skills/ieee-trans-rebuild/scripts/pagecompare.py \
    <源.pdf> main.pdf compare/ 100
```

- 目标：0 error、0 未解析引用（无 "??"）、**页数 = 原版**、每页图表落位同页同栏。
- 手段：浮动参数 `[!t]`/`[!b]`/`figure*`、`\newpage` 校正栏断点、`\IEEEtriggeratref` 平衡末页、必要处 `\vspace*{±pt}`。**最多 5 轮**；5 轮仍差 1–2 行属可接受（见 `references/06`）。
- 版面豁免（Elsevier pre-proof 重排为 IEEE 双栏）：只要求内容完整 + 页数接近，`audit.py --exempt <folder>` 标记。

## 阶段 6 · 打包

```bash
cd <工程> && zip <短名>_overleaf.zip main.tex sec_*.tex refs.tex IEEEtran.cls figures/*
```

zip 内必须有 `main.tex`、`IEEEtran.cls`、`figures/`（含 pdf+png）——上传 Overleaf 直接编译。

## 阶段 7 · 验收

```bash
~/anaconda3/envs/research/bin/python -I ~/.zcode/skills/ieee-trans-rebuild/scripts/audit.py \
    --root <工作区>/converted [--exempt <豁免文件夹>]
```

七项全过（见 `references/06`）→ 按模板写 `compare/report.md`；多篇任务汇总 `REPORT.md`（模板在 skill templates/）。

## 阶段 8 · 衔接

- 重建稿要润色/改写 → 用 personal-sci-writing skill（它的组内风格基线就来自这套重建语料）。
- 文献入库 → zotero skill `add_item`（DOI 已在阶段 1 核实过）。

## 关键常量速查

| 项 | 值 |
|---|---|
| 整页阅读渲染 | 180 dpi |
| 图表 raster 兜底 | 400 dpi |
| 对比图 | 100 dpi |
| 公式核验 zoom | 3.0（~216dpi）起步，争议处 6–10 倍 |
| 区域合并 | gap 8pt、最多 6 轮 |
| 最小区域 | 0.0008×页面积，宽/高 ≥15–20pt；>0.97×页面积视为整页背景丢弃 |
| `figure*` 阈值 | bbox 宽 > 0.62×页宽 |
| caption 提示 | fig./figure/table 开头块，竖直距离 < 60pt |
| 编译不合格线 | error>0、"??"、overfull > 20pt |
| 浮动调轮数上限 | 5 轮 |
