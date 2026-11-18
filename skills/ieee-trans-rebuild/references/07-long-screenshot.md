# 07 · 长截图（非 PDF 输入）管线

适用于：微信/网页长截图保存的文档（单栏、无文字层的整图）。实战先例：18 号微信 AI 对话长截图 1189×22337px → ctexart 中文转录，14/14 页。

## 1. 切页

```bash
~/anaconda3/envs/research/bin/python -I ~/.zcode/skills/ieee-trans-rebuild/scripts/slice_longscreenshot.py \
    <long.png> <工程>/ [--scale 2.0] [--target-px 1600]
```

- 策略：检测横向全空白带，在目标页高（默认 1600px ≈ A4@2x）附近择口切分，**避免切穿正文/公式**；窗口内无空白带才硬切。
- 产出：`pages/page_NN.png`（RGB）、`original_from_png.pdf`（切片合成，页尺寸 pt = px/scale）、`manifest.json`（pdf 字段指向合成的"原版"）。
- 合成 PDF 的作用：让 `pagecompare.py` 与 `audit.py` 的原版页数/对比图检查照常工作（长截图没有原生 PDF）。
- **切页后必须人眼翻一遍**：确认没有图被切穿；被切穿的图回源 PNG 用全局坐标重裁。

## 2. 插图裁剪

- 源是位图，无矢量可用：按估算 bbox 从**切片或源 PNG** 裁剪 → 自动去白边（min channel < 240，留 12px padding）→ `figures/figN_<desc>.png` + `crops.json` 记录。
- 注意 slice 与 Read 工具所见页码可能对错位，裁完逐张目检（边缘切字/混入正文行就调 bbox 重裁）。
- 源图里本来就模糊/被裁切的元素**忠实保留原状**（在 compare/report.md 记一条即可）。

## 3. 转录与排版

- 中文文档：`\documentclass[UTF8,a4paper,11pt]{ctexart}` + xelatex（首行 `% !TEX program = xelatex` 魔法注释让 Overleaf 自动选编译器；audit.py 据此豁免 IEEEtran.cls 检查）。
- 英文文档照常 IEEEtran（此时图片只能用位图，`\includegraphics` 不带扩展名）。
- **对话类源**（聊天记录）：正文与 UI 元素分离——时间戳/思考时长/气泡图标/附件气泡不复刻，用户提问以色块框复刻并标【用户提问】；文件引用条/网页来源条用灰色 chip 命令复刻（长文件名允许折行防溢出）。
- 无标题的源文档：整理者拟一个中性标题并在"转录说明"框中**显式声明哪些是整理者所加**——除声明外内容逐字保留（含原文语病）。
- 源图截断处：转录止于截断处 + 括注"源长截图在此截断"，不要脑补。

## 4. 常用排版元素对照

| 源元素 | LaTeX 复刻 |
|---|---|
| 步骤流程卡（带 ↓） | tcolorbox 圆角卡 + 居中行 + `$\downarrow$` |
| 高亮条目 | 卡内 `\colorbox{stepblue}{\begin{minipage}...\end{minipage}}` |
| 表格（浅灰横线） | booktabs 三线表 |
| 彩色节标题 | `\ctexset{section={format={...\color{headorange}}}}`；源自带"一、二、"序号时 `\setcounter{secnumdepth}{-1}` 关自动编号 |
| 灰色文件引用条 | `\colorbox` + minipage（\noindent 防 \parindent 溢出） |
| 用户提问气泡 | tcolorbox 无边框色块 |
| 无编号插图 | `figure[htbp]` + `\includegraphics`，不加 caption |

## 5. 验收差异

- 版面**必然豁免**（源是流式长图）：`audit.py --exempt <folder>`；七项中编译/引用/图片/对比图/zip 项照常检查。
- 对比图"逐页对齐"仅供内容核对（左原切片右重建页），不要求页界一致。
- 中英混排溢出：`\emergencystretch=3em`；chip 类命令注意 `\noindent`。
