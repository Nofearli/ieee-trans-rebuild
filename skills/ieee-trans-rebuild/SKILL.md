---
name: ieee-trans-rebuild
description: 把论文 PDF 逐页复刻重建为可编译的 IEEEtran LaTeX 工程（main.tex + 分节 sec_*.tex + 矢量图表 + 逐页对比图 + Overleaf zip），公式手写并高倍核验，IEEEtran.cls 内置。Use when the user asks PDF 转 LaTeX、论文重建、复刻 IEEE 排版、论文转 tex、把论文做成 Overleaf 工程、重建论文工程、PDF2LaTeX、ieee-trans-rebuild.
metadata:
  author: Nofearli
  version: "1.1.0"
  argument-hint: <pdf-or-png-path> [工作区目录]
---

# ieee-trans-rebuild · 论文 PDF → IEEE LaTeX 全流程复刻

输入一篇论文 PDF（或长截图 PNG），产出一个与原版逐页对齐、可直接上传 Overleaf 编译的 LaTeX 工程。
流程与验收标准来自 13 篇 IEEE 期刊稿（TAC/TAES/TCST/TCYB/TMech/TSMC/TNNLS/T-ASE/T-ITS + Elsevier 重排）与第二批 4 篇（IECON 会议稿 journal 重排、Automatica 重排、TCYB early access 逐页对齐、微信长截图 ctexart 转录）的实战重建，审计全部通过。

**第一次调用先读** `references/01-workflow.md`（端到端流程与常量），细节按需再查：

| 文件 | 内容 |
|---|---|
| references/01-workflow.md | 8 阶段流水线 + 关键常量速查 + 输入形态分支 |
| references/02-tex-conventions.md | 版面复刻（twoside、横幅水印、算法框、浮动控制） |
| references/03-formula-transcription.md | 公式手写 + zoom 高倍核验法（质量核心） |
| references/04-figure-extraction.md | 图表矢量裁剪与手工修正 |
| references/05-metadata-and-skills.md | 元数据核实链 + mineru/zotero/personal-sci-writing 集成 |
| references/06-acceptance.md | 审计七项 + 可接受/不可接受差异 |
| references/07-long-screenshot.md | 非PDF输入：长截图切页管线 + ctexart 中文转录 + audit xelatex 兼容 |

## 主工作流（单篇默认；多篇按篇滚动 + 最后汇总 REPORT）

0. **预检**：`pdflatex`、`~/anaconda3/envs/research/bin/python -I -c "import fitz"` 可用；建 `<工作区>/converted/<NN>_<短名>/`；`cp ~/.zcode/skills/ieee-trans-rebuild/assets/IEEEtran.cls <工程>/`
1. **元数据核实**：按 references/05 核实链查标题/作者/年份/DOI（Crossref→OpenAlex→zotero→web）；查不到标"待核实"，**绝不编造**
2. **资产提取**：`~/anaconda3/envs/research/bin/python -I ~/.zcode/skills/ieee-trans-rebuild/scripts/extract_assets.py <pdf> <工程>/ 180`
3. **mineru 预解析**：出 Markdown+LaTeX 底稿（敏感稿或无网跳过；底稿不直接采信）
4. **逐节转录**：读 pages/ + text/ + 底稿；`zoom.py` 拉公式高倍裁剪逐条核验；sec_*.tex 按原版分节；caption/文献逐字照抄；thebibliography 编号一一对应；伪代码框 ruled minipage；早期访问版版式复刻（twoside/横幅/水印）
5. **编译对齐**：pdflatex ×2 → 0 error/0 "??"；`pagecompare.py <原.pdf> main.pdf compare/ 100`；浮动体微调 ≤5 轮至页数与图表落位一致（Elsevier pre-proof 重排豁免页数）
6. **打包**：`zip <短名>_overleaf.zip main.tex sec_*.tex refs.tex IEEEtran.cls figures/*`
7. **验收**：`audit.py --root <工作区>/converted`；按 templates/compare_report_template.md 写 compare/report.md；多篇任务按 templates/REPORT_template.md 汇总
8. **衔接**：提示可用 personal-sci-writing 润色；zotero add_item 入库

## 已知坑（务必记住）

- **PDF 文字层系统性丢希腊字母/上下标**：只当代码辅助，公式以 zoom 裁剪核验的手写为准
- **IEEEtran journal 默认 oneside**：早期访问稿原版奇偶页 running head 镜像，必须加 `twoside`
- 转录派子代理时可能被内容安全过滤器反复中断（博弈/军事类论文常见）→ 由主代理直接续写兜底，不要反复重试
- 单栏 Elsevier 版式下 extract_assets 自动检测基本失效 → 走 references/04 手工 crops
- Elsevier pre-proof 水印是嵌入 XObject → 在**工作副本**上清除后裁剪，原始 PDF 永不修改
- 脚本一律 `~/anaconda3/envs/research/bin/python -I` 运行

## 边界

- 只做忠实复刻：逐字照抄（含原版 typo），不做语言润色（润色转 personal-sci-writing）
- 不编造任何元数据、数据、文献
- 原始 PDF 永不修改
- 图内文字随裁剪带入；ORCID 图标等平台图形元素不复刻（记入遗留差异）
