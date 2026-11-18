# 05 · 元数据核实 + 其他 skill 集成点

## 1. 元数据核实链（阶段 1 执行）

来源优先级（命中即停，全查不到则标"待核实"）：

1. **PDF 首页**：标题、作者、单位、收稿日期（"Manuscript received ..." 里常含年份线索）、DOI 脚注、期刊名/卷期。
2. **DOI 反查**：`curl -s https://api.crossref.org/works/<DOI>` → 标题/作者/年份/期刊。
3. **Crossref 按标题检索**：`curl -s "https://api.crossref.org/works?query.title=<标题>&rows=3"`。
4. **OpenAlex**：`curl -s "https://api.openalex.org/works?search=<标题>"`。
5. **zotero skill**（Zotero 在跑时）：`search_library` 全文/标题检索，命中可直接 `add_item` 归档（identifier 传 DOI）。
6. **Web 搜索**：标题 + 作者 + 期刊关键词。

规则：
- **绝不编造**。查不到 → 文件名保留"年份待核实/作者待核实"标记，工程 main.tex 作者块留 `Authors\ TBD`，上方 `% TODO(作者待核实):` 注释逐条列出已查渠道与结果（先例：T-ASE 早期访问稿 5 渠道全空）。
- 核实到的元数据写进 compare/report.md，并把 DOI 顺手做 zotero `add_item`。

## 2. mineru（阶段 3，解析底稿）

- 调用：mineru skill，输入源 PDF，产出 Markdown + LaTeX 公式草稿（`--output` 到工程的 `mineru_draft/`）。
- 何时用：默认跑（省打字）；**PDF 含未发表/敏感内容时跳过**（会上传 MinerU 云端）。
- 采信边界：只作段落结构/文献列表/公式打字底稿；公式逐条按 references/03 核验后才可进 main.tex。
- 云端不可用/无 token 时：跳过，纯手写转录（原 13 篇即此流程，质量无差）。

## 3. zotero（阶段 1 与阶段 8）

- 阶段 1：`search_library` 辅助核实作者/年份；比对本地库是否已有该文。
- 阶段 8：核实到 DOI 后 `add_item`（自动带 arXiv PDF）；用户有指定 collection 就加进去。

## 4. personal-sci-writing（阶段 8，下游衔接）

重建完成、用户要改写/润色时转交该 skill：它按个人硬规则 + 课题组 IEEE 风格基线诊断改写。
注意边界：重建任务只做忠实复刻（逐字照抄），**不做语言润色**；润色是重建之后的独立动作。

## 5. 何时都不用

若环境缺网/缺 skill，全流程仍可手写完成（mineru/zotero 都是可选加速项；audit/extract/pagecompare/zoom 四个脚本仅依赖本地 PyMuPDF + Pillow）。
