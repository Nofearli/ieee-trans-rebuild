# 论文 PDF → IEEE LaTeX 重建总报告

**范围**: `<工作区>` 下 N 个 PDF（跳过与正式版重复的审稿副本），共 **M 篇** 重建为 IEEEtran LaTeX 工程
**完成时间**: YYYY-MM-DD
**验收方式**: 统一审计脚本 `audit.py --root`（七项）+ 每篇逐页对比图人工复查
**审计结果**: **M/M 全部 OK**

## 一、总览表

| # | 文件夹 | 期刊 | 原页 | 新页 | 编号公式 | 图 | 文献 | 状态 |
|---|---|---|---|---|---|---|---|---|
| 01 | 01_<短名> | IEEE XXX | N | N | X | X | X | OK |

- 各篇页数与原版一致；版面豁免篇（如 Elsevier pre-proof 重排）在此注明豁免理由。
- 全部 M 篇：编译 0 error、0 未解析引用、PDF 文字层无 "??"、无缺失图片引用。

## 二、每篇交付物（结构统一）

```
latex_converted/<序号_短名>/
├── main.tex                 # preamble + 标题/作者/脚注 + 章节 \input
├── sec_*.tex                # 按原版分节拆分
├── refs.tex                 # thebibliography 逐条照抄（编号与原版一致）
├── figures/                 # 从原 PDF 矢量裁剪的图表（+png 兜底）
├── main.pdf                 # 重建版
├── compare/
│   ├── report.md            # 该篇指标表 + 逐页对比图 + 遗留差异
│   └── compare_pNN.png      # 逐页左右对比图（左原版/右重建）
└── <短名>_overleaf.zip      # tex + figures + IEEEtran.cls，上传 Overleaf 即编译
```

## 三、质量指标汇总

| 指标 | 结果 |
|---|---|
| 审计通过率 | M/M |
| 页数一致性 | X/X（豁免 Y 篇） |
| 编译错误 / 未解析引用 | 全部 0 |
| Overfull > 20pt | 全部 0 |
| 图片引用缺失 | 全部 0 |
| 可独立编译的 zip | M/M |
| 公式处理方式 | 手写 LaTeX + 高倍裁剪逐条核验（mineru 底稿仅作参考，不直接采信） |
| 参考文献 | thebibliography 逐条照抄，编号与原版一一对应 |

## 四、跨篇通用做法与已知差异

<引用 skill references/06-acceptance.md 的"可接受差异"清单，按本批实际出现情况记录>

## 五、元数据待核实项

<有"年份待核实/作者待核实"的篇目列出：核查了哪些渠道、结论；无则写"无">
