# 02 · LaTeX 版面复刻规则

目标：重建版与原版**页数一致、每页图表落位同页同栏**。以下规则来自 13 篇 IEEE 稿的实战。

## 1. 文档类

- 正式出版稿：`\documentclass[journal]{IEEEtran}`。
- **早期访问稿（accepted article / Xplore 在线版）必须加 `twoside`**：`\documentclass[journal,twoside]{IEEEtran}` —— IEEEtran journal 默认 oneside，而早期访问原版奇偶页 running head 镜像，不加则页眉错。
- 非期刊变体：会议稿 `conference`；Elsevier 原稿重排仍用 `journal`（内容完整优先，版面豁免）。

## 2. 标题区

- `\title/\author/\markboth/\thanks` 与原版逐字符一致；`~\IEEEmembership{...}`、基金脚注 `\thanks{...}` 按原版首页排。
- 首页版权块/横幅（accepted article 的 "Accepted for publication" 条、Xplore 首页块）：按原版字符坐标用 `\thanks` 脚注或盒子复刻。
- 首页无作者名的早期访问稿（如 T-ASE 在线版）：`\author{Authors\ TBD}` + `% TODO(作者待核实)` 注释记录核查渠道，**不编造**。

## 3. 版面几何（仅逐页对齐需要时）

从原版 PDF 量出（fitz `page.get_text("dict")` 或量 bbox），硬编码进 preamble，例（TAES 2025 实测值）：

```latex
\setlength{\textwidth}{490.2pt}\setlength{\columnsep}{12pt}
\setlength{\textheight}{684pt}\setlength{\topmargin}{-60.9pt}
\setlength{\parindent}{14.8pt}
% 浮动容量放宽，保证大图都能落 top：
\setcounter{topnumber}{4}\setcounter{totalnumber}{5}
\renewcommand{\topfraction}{0.99}\renewcommand{\textfraction}{0.01}
\renewcommand{\floatpagefraction}{0.99}
```

- running head 位置与原版不符时（早期访问版有的把页眉放页脚）：重定义 `\ps@headings` / `\ps@IEEEtitlepagestyle` 复刻。
- Xplore 页脚水印：`eso-pic` 的 `\AddToShipoutPictureFG` 每页画水印字符串（字符坐标取自原版）。

## 4. 浮动体与图表落位

- 跨栏大图/表：`figure*` / `table*`（判据：宽 > 0.62×页宽，manifest 已标 `spans_columns`）。
- 同页多图：按原版拆块后合并进同一 float，或 float 内 `\\[gap]` 手工堆叠；子图保持原版编号方式（subfig/caption 手写均可，落位优先）。
- 栏断点不对：`\newpage` 校正；图表晚一页：改 `[!t]`↔`[!b]`、调整 float 出现位置（LaTeX float 不能早于首次引用前的合理位置，可把 source 位置前移）。
- 局部高度微调：`\vspace*{-5pt}` 级别补偿（实测用到 -5 ~ -24pt；`\abovecaptionskip=0pt` 常用）。**尽量不用 `\enlargethispage`**。
- 末页参考文献两栏平衡：`\IEEEtriggeratref{N}`（N = 触发换栏的文献序号，试到两栏齐平）。

## 5. 伪代码/算法框

**一律手工 ruled `minipage` 复刻**（含顶线/底线粗细、标题是否加粗），不用 `algorithm` 浮动体——IEEEtran 的 algorithm float 框线结构与原版不一致：

```latex
\noindent\begin{minipage}{\columnwidth}
\rule{\columnwidth}{0.8pt}\\[2pt]
\textbf{Algorithm 1:} <标题>\\
\rule{\columnwidth}{0.4pt}\\
\begin{algorithmic}[1]
...
\end{algorithmic}\\
\rule{\columnwidth}{0.8pt}
\end{minipage}
```

## 6. 定理环境

自定义样式对齐原版（IEEE 常见：小型大写标题 + 正体正文）：

```latex
\makeatletter
\newtheoremstyle{ieeestyle}{6pt}{6pt}{\upshape}{}{\scshape}{.}{.5em}{}
\makeatother
\theoremstyle{ieeestyle}
\newtheorem{theorem}{Theorem}
```

## 7. 忠实复刻的边界

- **逐字照抄**：摘要、caption、脚注、文献、致谢；原版 typo 保留（如 11 号篇 "Tacking errors" 原样保留）。
- **不复制刻**：图内文字（随矢量裁剪带入）、ORCID 图标等出版平台图形元素。
- 正文断行允许与原版有 1–4 行偏移（页码/公式编号/图表落页必须一致）；分式可用紧凑形式换整页落位。
