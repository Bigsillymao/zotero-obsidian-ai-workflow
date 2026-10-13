---
name: doc-to-md
description: 读取 PDF、图片、扫描件、Word/PPT/HTML 等文档前，先用 MinerU 转换为 Markdown 再阅读；xlsx/csv（含伪装成 .xls 的 HTML 表格）转 Markdown 表格。当用户要求读 PDF/文档/论文/表格，或需要提取文档内容与表格时使用。Use before reading any PDF / scanned / Office / HTML document, or converting spreadsheet tables to Markdown.
---

# doc-to-md：文档先转 Markdown 再读

直接把 PDF / 扫描件 / 表格交给模型，容易丢表格结构、乱码、页码对不上。
先转 Markdown 再读：表格保留为 Markdown 表格，每页带 `<!-- page N of M -->` 定位标记，结论可精确溯源。

## 何时使用

- 读取任何 PDF / 扫描件 / 图片型文档 / Word / PPT / HTML 的内容
- 从文档中提取表格（含复杂表格、跨页表格）
- 浏览 xlsx / csv 表格内容

## 流程 1：文档 → MinerU 4.x → Markdown

脚本位于本技能目录的 `scripts/` 下（下文以 `<skill-dir>` 代指本技能所在目录，例如 `C:\Users\you\.zcode\skills\doc-to-md`）。

Windows（PowerShell）：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "<skill-dir>\scripts\to-md.ps1" -InputPath "<文件路径>"
```

Linux / macOS / Git Bash：

```bash
"<skill-dir>/scripts/to-md.sh" "<文件路径>"
```

参数（两平台一致）：

| 参数 | 说明 |
| --- | --- |
| `-OutFile` / `-o` | 输出路径；默认源文件旁 `<文件名>_md.md` |
| `-Pages` / `-p` | 选页：`all`（默认）\| `1-5,8` \| `r3-r1`（倒数）。**仅对 PDF 生效**，非 PDF 自动省略（MinerU 拒绝非 PDF 的 `--pages`）；注意 MinerU 原生默认只转前 10 页 |
| `-Tier` / `-t` | `flash`（默认，离线秒级）\| `basic` \| `standard` \| `advanced`（首用下模型） |
| `-Remote` / `-r` | 走 mineru.net 云端解析 |
| `-MineruExe` | 指定 mineru 可执行文件；亦可用环境变量 `MINERU_EXE` |

支持 PDF / 图片 / 扫描件 / Word / PowerPoint / HTML；非 PDF 一律整文档解析。

**前置：本地解析服务需先启动**（每次开机一次；`flash` 档离线解析必需）：

```bash
mineru server start    # 启动（报"服务已启动"即可）
mineru server status   # 查看状态
mineru server stop     # 停止
```

未启动会报「Local parse-server is disabled」。

## 流程 2：表格 → Markdown 表格

```powershell
python "<skill-dir>\scripts\xlsx-to-md.py" "<文件路径>"
```

- 支持 `.xlsx` / `.csv`
- `.xls` 自动探测：**伪装成 .xls 的 HTML 表格**（高校教务 / 综测系统等系统导出常见）会被自动识别并解析（colspan/rowspan 展开；需要 `pip install beautifulsoup4`）；真·二进制 `.xls` 会提示先转 `.xlsx`
- `.html` / `.htm` 中的 `<table>` 也能转

⚠ **数值红线**：转换出的 Markdown 只用于阅读；**数据校核、定案值引用必须读原始文件（Excel 等）的精确值**。

## 兜底与已知坑

- 「Local parse-server is disabled」→ 先 `mineru server start`，或改用 `-Tier flash`
- mineru 找不到 → `pip install "mineru[core]"`，或用 `-MineruExe` / `MINERU_EXE` 指定路径
- 非 PDF 文件（docx / 图片等）报 `Page range is only supported for PDF files` → `--pages` 仅支持 PDF；本技能脚本已按类型自动省略，手工调用时注意别传
- 报 `cas-server.xethub.hf.co` 401 / `File reconstruction error` → 模型源被解析成 huggingface 且走了 Xet 通道：把 `~/.mineru/config.yaml` 写为 `model: source: modelscope`（或服务启动前 `MINERU_MODEL_SOURCE=modelscope`），重启 `mineru server`
- 文件名含中文引号（如 `附件1：…doc`）时，bash 引号易配对失败 → 先复制成无引号文件名再处理
- 真·老格式 `.xls` → `soffice --headless --convert-to xlsx "old.xls"` 后再转
- 修改 `to-md.ps1` 时保持**纯 ASCII**：Windows PowerShell 5.1 会把无 BOM 的 UTF-8 脚本当 GBK 读
