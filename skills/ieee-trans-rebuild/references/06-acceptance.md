# 06 · 验收标准与可接受差异

## 1. 审计七项（audit.py，全过才算完）

| # | 检查 | 不合格线 |
|---|---|---|
| 1 | 页数：manifest 源 PDF vs main.pdf | 不一致（`--exempt` 豁免的除外） |
| 2 | 编译日志 main.log | `^! ` 错误 >0；`Reference/Citation undefined` >0；Overfull hbox > 20pt |
| 3 | 渲染 PDF 文字层 | 出现 "??"（未解析引用） |
| 4 | `\includegraphics` 目标 | 任何 .pdf/.png 落空 |
| 5 | compare/report.md | 缺失 |
| 6 | compare_pNN.png | 数量 < 重建页数 |
| 7 | zip | 缺 main.tex / IEEEtran.cls / figures/*.pdf |

```bash
~/anaconda3/envs/research/bin/python -I ~/.zcode/skills/ieee-trans-rebuild/scripts/audit.py \
    --root <工作区>/converted [--exempt <folder> ...] [folder ...]
```

豁免用于非 IEEE 版式重排（Elsevier pre-proof 等）：跳过页数检查，其余六项仍必须全过。

## 2. 每篇交付物核对单

- [ ] main.tex + sec_*.tex + refs（文献编号与原版一一对应）
- [ ] figures/（矢量 pdf + png 兜底）
- [ ] main.pdf（页数=原版；图表落位同页同栏）
- [ ] compare/report.md + compare_pNN.png（左原版右重建）
- [ ] `<短名>_overleaf.zip`（上传即编译）
- [ ] 元数据 TODO 项全部记录核查渠道

## 3. 可接受差异（写入 report.md，不算失败）

1. 正文断行与生产排版不完全逐行一致：栏内断点 1–4 行偏移（页码、公式编号、图表所在页必须一致）。
2. 生产排版的整尺寸分式在 LaTeX 中用紧凑分式（`\tfrac`）换落位。
3. 图内文字（坐标轴、图例、照片标注）随矢量裁剪带入，不重排。
4. ORCID 图标等出版平台图形元素不复刻。
5. 浮动体 5 轮内调不平的 1–2 行页内漂移（有 `\vspace*` 微调记录）。

## 4. 不可接受（必须修）

- 编译 error、未解析引用、"??"
- 页数不符（豁免篇除外）
- 图表落错页/错栏
- 文献编号错位、caption 与原版文字不符
- 公式未经 zoom 核验直接采信文字层/mineru
- 元数据编造
