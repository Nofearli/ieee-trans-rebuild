# <论文标题> — 重建对比报告

**期刊/会议**: <IEEE XXX 年份> ｜ **原版页数**: N ｜ **重建页数**: N
**源 PDF**: `<路径>` ｜ **工程**: `latex_converted/<NN_短名>/`

## 一、结果概览

| 指标 | 原版 | 重建 |
|---|---|---|
| 页数 | N | N |
| 图 | X | X |
| 表 | X | X |
| 编号公式 | X | X |
| 无编号公式 | X | X |
| 定理类环境 | X | X |
| 参考文献 | X | X |
| 作者简介 | X | X |
| 编译 | — | 0 error / 0 未解析引用 |

## 二、逐页对齐说明

每页图表落位与原版一致；对比图左原版右重建：

| 页 | 内容 | 对比图 |
|---|---|---|
| 1 | 标题/摘要/引言开头 | ![p1](compare_p01.png) |
| 2 | ... | ![p2](compare_p02.png) |

## 三、量化校验

- 全文文字层词数：原版 N vs 重建 N（diff 仅连字符断行与字形伪影，`difflib` 逐词比对）
- 公式：全部手写 amsmath，逐条对照 zoom 高倍裁剪核验，无 OCR 兜底
- 图表：PyMuPDF 矢量裁剪（400dpi png 兜底），手工修正 bbox 的有：<列出>

## 四、版面微调记录

- <例：p3 图 A `\vspace*{-5pt}`；`\abovecaptionskip=0pt`；display-skip 补偿>
- <全文无 `\enlargethispage`（或列出用了哪页）>

## 五、遗留差异清单

1. <例：正文断行与生产排版不完全逐行一致，p4 栏内断点偏移 2 行（页码/公式号/图表落页一致）>
2. <例：全尺寸分式改紧凑分式>
3. <图内文字随原版裁剪带入，不重排>

## 六、工程文件

main.tex + sec_*.tex + refs.tex + figures/ + main.pdf + IEEEtran.cls + compare/ + `<短名>_overleaf.zip`
