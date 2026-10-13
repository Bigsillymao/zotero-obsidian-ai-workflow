# doc-to-md

**让 AI 先"读懂"，再回答：把 PDF / 扫描件 / Office / 表格先转成 Markdown，再交给模型阅读。**

一个通用 [Agent Skill](https://code.claude.com/docs/en/skills)（Claude Code / ZCode 等 agent 加载 `SKILL.md` 即用），
附两个零依赖的命令行脚本，Windows 与 Linux / macOS 双平台。

## 为什么

把 PDF 直接甩给模型，常见翻车：表格丢结构、扫描件根本读不出、页码对不上、中文乱码。
**先转 Markdown 再读**：

- 表格保留为 Markdown 表格，复杂 / 跨页表格合并还原
- 扫描件、图片型文档走 OCR
- 每页带 `<!-- page N of M -->` 定位标记，结论可精确溯源
- 纯文本对模型更稳、更省 token

## 功能

| 输入 | 输出 | 引擎 |
| --- | --- | --- |
| PDF / 图片 / 扫描件 / docx / pptx / html | Markdown（页标记、表格、公式） | [MinerU](https://github.com/opendatalab/MinerU) 4.x |
| xlsx / csv | 每个工作表一节 Markdown 表格 | openpyxl（脚本） |
| 伪装成 `.xls` 的 HTML 表格（各类系统导出常见） | 自动识别并转 Markdown 表格，colspan/rowspan 展开 | beautifulsoup4（脚本） |

## 安装

**1. MinerU**（Python 3.10+）：

```bash
pip install "mineru[core]"
mineru server start        # 每次开机后启动本地解析服务（flash 档离线解析必需）
```

**2. 本技能**：把本仓库放进 agent 的 skills 目录，例如：

```bash
git clone https://github.com/Bigsillymao/zotero-obsidian-ai-workflow ~/.zcode/skills/doc-to-md     # ZCode
git clone https://github.com/Bigsillymao/zotero-obsidian-ai-workflow ~/.claude/skills/doc-to-md    # Claude Code
```

也可以不装技能，直接把 `scripts/` 当普通命令行工具用。

**3. 可选**：`pip install beautifulsoup4`（解析伪装 .xls 的 HTML 表格时需要）。

## 用法

### PDF / Office / 扫描件 → Markdown

```powershell
# Windows
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\to-md.ps1 -InputPath "论文.pdf"
```

```bash
# Linux / macOS / Git Bash
./scripts/to-md.sh "论文.pdf"
```

| 参数 | 说明 |
| --- | --- |
| `-o, --out` | 输出路径；默认源文件旁 `<文件名>_md.md` |
| `-p, --pages` | 选页：`all`（默认）\| `1-5,8` \| `r3-r1`（倒数）。MinerU 原生默认只转前 10 页 |
| `-t, --tier` | `flash`（默认，离线秒级）\| `basic` \| `standard` \| `advanced`（首用自动下模型） |
| `-r, --remote` | 走 mineru.net 云端解析 |
| `-MineruExe` | 指定 mineru 可执行文件；亦可用环境变量 `MINERU_EXE` |

### 表格 → Markdown 表格

```bash
python scripts/xlsx-to-md.py "成绩单.xlsx"
python scripts/xlsx-to-md.py "综测导出.xls"     # 自动识别 HTML 伪装
python scripts/xlsx-to-md.py data.csv
```

> ⚠ 数值红线：Markdown 仅供阅读与喂给模型；**数据校核、定案值引用必须回原始文件读精确值**。

## 实测坑位（都是真金白银）

| 症状 | 原因 / 解法 |
| --- | --- |
| `Local parse-server is disabled` | 本地解析服务没起：`mineru server start`（每次开机一次） |
| `mineru not found` | 没装或不在 PATH：`pip install "mineru[core]"`；或设 `MINERU_EXE` 指定 |
| `.ps1` 中文乱码 / 报奇怪的错 | PowerShell 5.1 把无 BOM 的 UTF-8 当 GBK 读：脚本内容保持纯 ASCII |
| 真 `.xls` 转出空表 | 老二进制格式不直接支持：`soffice --headless --convert-to xlsx` 先转 |
| `.xls` 打开是网页源码 | 系统导出的是 HTML 伪装 `.xls`：本仓库脚本已自动识别处理 |
| 非 PDF（docx / 图片）报 `Page range is only supported for PDF files` | `--pages` 参数只允许 PDF：本仓库脚本已按文件类型自动省略；手工调用 MinerU 时注意 |
| standard/advanced 首次很慢 | 在下载模型；默认 `MINERU_MODEL_SOURCE=modelscope`（国内镜像），可改 `huggingface` |
| `File reconstruction error ... 401 Unauthorized`（域名 `cas-server.xethub.hf.co`） | 模型源被解析成 huggingface 并走了 hf-xet 的 Xet 通道（hf-mirror 等镜像不覆盖该域名）。把 `~/.mineru/config.yaml` 写为 `model: source: modelscope`（或服务启动前设 `MINERU_MODEL_SOURCE=modelscope`），再 `mineru server stop && mineru server start` |

## 实测环境与验证

- 开发/实测环境：Windows 11 + MinerU 4.0.12（Python 3.10.4），PowerShell 5.1 / Git Bash
- 已端到端实测（2026-10-13）：
  - PDF → Markdown：`to-md.ps1`、`to-md.sh` 均通过（含 `-Pages` 参数）；模型缓存后单页约 2 秒
  - Word（.docx）→ Markdown：标题 / 段落 / 表格完整保留
  - 图片（.png，扫描件路线）→ Markdown：flash 档 OCR 可用
  - xlsx（多工作表）/ GBK 编码 csv / HTML 伪装 `.xls`（含 colspan 展开）/ 真 `.xls` 引导分支：全部通过
  - 中文 + 空格文件名：通过
- flash 档首次使用会从 modelscope 下载模型（实测约 226 MB，缓存在 `~/.mineru/models/`），之后离线秒级
- `to-md.sh` 在 Git Bash 实测通过；Linux / macOS 未实测（仅包装同一 CLI）
- 自测样例可再生成：`python tests/make_test_files.py`（PDF 样例需 LibreOffice 或自备 PDF）。⚠ 测试产物目录 `tests/_fixtures/` 已在 `.gitignore` 中——**不要提交或上传测试产物**（二进制样例可能带转换工具写入的文档属性）

## English Quick Start

A portable Agent Skill + CLI wrappers that convert documents to Markdown **before** an LLM reads them.

```bash
pip install "mineru[core]" && mineru server start     # parse server: once per boot
./scripts/to-md.sh paper.pdf                          # -> paper_md.md (page markers, tables kept)
./scripts/to-md.sh paper.pdf -t standard -p '1-5'     # higher quality tier, first 5 pages
python scripts/xlsx-to-md.py data.xlsx                # also .csv and HTML-masqueraded .xls
```

- Tiers: `flash` (default, offline) | `basic` | `standard` | `advanced` (models download on first use)
- `MINERU_EXE` overrides the mineru path; `MINERU_MODEL_SOURCE` switches the model mirror (default `modelscope`)
- Numbers in the generated Markdown are for reading only — verify against the source file before formal use.

## License

MIT — see [LICENSE](LICENSE).
