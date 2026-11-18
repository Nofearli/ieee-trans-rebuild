# ieee-trans-rebuild

论文 PDF → IEEE LaTeX 全流程重建 skill。输入一篇论文 PDF，按已验证的实战流程（13 篇 IEEE 期刊稿重建、审计 13/13 通过）产出与原版**逐页对齐**、可直接上传 Overleaf 编译的 LaTeX 工程。

## 它做什么

给定 `paper.pdf`，产出：

```
converted/<NN_短名>/
├── main.tex + sec_*.tex + refs.tex   # 手写转录，公式逐条对照高倍裁剪核验
├── figures/                          # 从原 PDF 矢量裁剪（+400dpi png 兜底）
├── main.pdf                          # 重建版，页数与图表落位对齐原版
├── IEEEtran.cls                      # V1.8b 内置，换机/Overleaf 都能编译
├── compare/                          # 逐页左右对比图 + 对比报告
└── <短名>_overleaf.zip               # 上传即编译
```

特色：

- **忠实复刻**：摘要/caption/文献逐字照抄，`thebibliography` 编号与原版一一对应；早期访问稿复刻 accepted-article 横幅、Xplore 水印、twoside 页眉镜像
- **公式质量**：全部手写 LaTeX，逐条对照 3–10 倍 zoom 裁剪核验（不信任文字层/mineru 的希腊字母）
- **机器验收**：`audit.py` 七项审计（页数/编译错误/未解析引用/超宽/缺图/对比图/zip 内容）
- **skill 协作**：mineru 预解析底稿（可选）、zotero 元数据核实与入库、personal-sci-writing 下游润色

## 安装

将 `skills/ieee-trans-rebuild` 放入技能目录（ZCode 为 `~/.zcode/skills/`）。

依赖（本机已具备）：

- TeX Live：`texlive-base` + `texlive-publishers`（pdflatex；IEEEtran.cls 已内置，装不上 publishers 也能跑）
- Python：PyMuPDF + Pillow（建议 `~/anaconda3/envs/research/bin/python`，脚本均以 `-I` 调用）

## 使用

对 agent 说：「用 ieee-trans-rebuild 把这篇论文转成 LaTeX」+ PDF 路径即可。手动调用脚本：

```bash
PY=~/anaconda3/envs/research/bin/python
S=~/.zcode/skills/ieee-trans-rebuild

$PY -I $S/scripts/extract_assets.py paper.pdf converted/01_demo/ 180   # 资产提取
$PY -I $S/scripts/zoom.py paper.pdf --page 3 --column left --zoom 3    # 公式高倍裁剪
$PY -I $S/scripts/pagecompare.py paper.pdf converted/01_demo/main.pdf converted/01_demo/compare/ 100
$PY -I $S/scripts/audit.py --root converted/ --exempt 01_demo_elsevier # 验收审计
```

流程细节见 [`skills/ieee-trans-rebuild/references/`](skills/ieee-trans-rebuild/references/)（8 阶段流水线、版面复刻规则、公式核验法、图表裁剪、元数据核实链、验收标准）。

## 边界

- 只做忠实复刻（含原版 typo），不做语言润色——润色请用 [personal-sci-writing](https://github.com/Nofearli/personal-sci-writing)
- 不编造元数据/数据/文献；查不到就标"待核实"并记录已查渠道
- 原始 PDF 永不修改；Elsevier 水印只在**工作副本**上清除
- 非 IEEE 版式（Elsevier pre-proof 等）重排为 IEEE 双栏时页数豁免，内容完整性优先
