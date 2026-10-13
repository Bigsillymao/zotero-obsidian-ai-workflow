> 🌐 [简体中文](README.md) | **English**

# doc-to-md

**Let the AI actually read your documents: convert PDF / scans / Office files / spreadsheets to Markdown before the model sees them.**

A universal [Agent Skill](https://code.claude.com/docs/en/skills) (works in Claude Code, ZCode and other
agents — just load `SKILL.md`), shipped with two dependency-light command-line wrappers for Windows and Linux/macOS.

## Why

Handing a PDF straight to a model usually goes wrong: tables lose their structure, scans are unreadable,
page numbers don't line up. **Convert to Markdown first**:

- tables stay real Markdown tables — complex and multi-page tables are merged and recovered
- scans and image-based documents go through OCR
- every page carries a `<!-- page N of M -->` marker, so conclusions stay traceable
- plain text is friendlier to models and cheaper in tokens

## Features

| Input | Output | Engine |
| --- | --- | --- |
| PDF / images / scans / docx / pptx / html | Markdown (page markers, tables, formulas) | [MinerU](https://github.com/opendatalab/MinerU) 4.x |
| xlsx / csv | one Markdown table section per worksheet | openpyxl (script) |
| HTML tables masquerading as `.xls` (common in system exports) | auto-detected, converted to Markdown tables with colspan/rowspan expansion | beautifulsoup4 (script) |

## Install

**1. MinerU** (Python 3.10+):

```bash
pip install "mineru[core]"
mineru server start        # start the local parse server (required for offline 'flash' parsing)
```

**2. This skill** — drop the repository into your agent's skills directory, e.g.:

```bash
git clone https://github.com/Bigsillymao/doc-to-md ~/.zcode/skills/doc-to-md     # ZCode
git clone https://github.com/Bigsillymao/doc-to-md ~/.claude/skills/doc-to-md    # Claude Code
```

You can also skip the skill and use `scripts/` as plain command-line tools.

**3. Optional**: `pip install beautifulsoup4` (needed to parse HTML-masqueraded `.xls` files).

## Usage

### PDF / Office / scans → Markdown

```powershell
# Windows
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\to-md.ps1 -InputPath "paper.pdf"
```

```bash
# Linux / macOS / Git Bash
./scripts/to-md.sh "paper.pdf"
```

| Option | Meaning |
| --- | --- |
| `-o, --out` | output path; defaults to `<filename>_md.md` next to the source |
| `-p, --pages` | page selection: `all` (default) \| `1-5,8` \| `r3-r1` (from the end). MinerU natively converts only the first 10 pages |
| `-t, --tier` | `flash` (default, offline, seconds) \| `basic` \| `standard` \| `advanced` (models download on first use) |
| `-r, --remote` | parse via the mineru.net cloud service |
| `-MineruExe` | explicit path to the mineru executable; or set the `MINERU_EXE` environment variable |

### Spreadsheets → Markdown tables

```bash
python scripts/xlsx-to-md.py "grades.xlsx"
python scripts/xlsx-to-md.py "export.xls"      # auto-detects the HTML masquerade
python scripts/xlsx-to-md.py data.csv
```

> ⚠ Numbers red line: the generated Markdown is for reading and for feeding models only; **data
> verification and final quoted values must be read from the original files**.

## Field-tested pitfalls

| Symptom | Cause / fix |
| --- | --- |
| `Local parse-server is disabled` | the local parse server is not running: `mineru server start` (once per boot) |
| `mineru not found` | not installed or not on PATH: `pip install "mineru[core]"`; or point `MINERU_EXE` at it |
| MinerU installed but rejects flags (e.g. global `-p`/`-o`) | 3.x and earlier use a different CLI than 4.x: check `mineru --version`; this repo targets the 4.x subcommand style — upgrade with `pip install -U "mineru[core]"` |
| `.ps1` garbled / weird errors | PowerShell 5.1 reads BOM-less UTF-8 as GBK: keep script contents pure ASCII |
| Real `.xls` converts to an empty table | the old binary format is not supported directly: convert first with `soffice --headless --convert-to xlsx` |
| `.xls` opens as web-page source | the system exported an HTML-masqueraded `.xls`: the scripts here detect and handle it automatically |
| Non-PDF (docx / image) fails with `Page range is only supported for PDF files` | `--pages` is PDF-only in MinerU: the wrappers omit it automatically per file type; keep that in mind when calling MinerU by hand |
| First `standard`/`advanced` run is very slow | it is downloading models; the default is `MINERU_MODEL_SOURCE=modelscope` (fast in China), switchable to `huggingface` |
| `File reconstruction error ... 401 Unauthorized` (domain `cas-server.xethub.hf.co`) | the model source resolved to huggingface and went through hf-xet's Xet channel (not covered by mirrors like hf-mirror). Write `model: source: modelscope` into `~/.mineru/config.yaml` (or set `MINERU_MODEL_SOURCE=modelscope` before starting the server), then `mineru server stop && mineru server start` |

## Tested environment & verification

- Developed and verified on: Windows 11 + MinerU 4.0.12 (Python 3.10.4), PowerShell 5.1 / Git Bash
- End-to-end tested (2026-10-13):
  - PDF → Markdown: both `to-md.ps1` and `to-md.sh` pass (including the `-Pages` option); ~2 seconds per page once models are cached
  - Word (.docx) → Markdown: headings, paragraphs and tables fully preserved
  - Image (.png, the scan route) → Markdown: flash-tier OCR works
  - xlsx (multiple worksheets) / GBK-encoded csv / HTML-masqueraded `.xls` (colspan expansion) / real-`.xls` guidance branch: all pass
  - Chinese and space-containing filenames: pass
- The first flash-tier run downloads models from modelscope (~226 MB measured, cached under `~/.mineru/models/`); afterwards it is offline and takes seconds
- `to-md.sh` was tested in Git Bash; Linux / macOS not tested (it only wraps the same CLI)
- Test fixtures can be regenerated: `python tests/make_test_files.py` (the PDF sample needs LibreOffice, or bring your own PDF). ⚠ `tests/_fixtures/` is in `.gitignore` — **never commit or upload test artifacts** (binary samples may carry document properties written by conversion tools)

## License

MIT — see [LICENSE](LICENSE).
