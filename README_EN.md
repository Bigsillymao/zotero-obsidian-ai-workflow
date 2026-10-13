> 🌐 [简体中文](README.md) | **English**

# Zotero + Obsidian + AI — a research knowledge workflow

**Turn papers into knowledge, data into figures, and documents into readable text.**
An AI assistant sits in the middle: Zotero is the literature entry point, Obsidian is the long-term
knowledge base, plus two side pipelines — scientific plotting (Origin only) and file conversion (→ Markdown).

> This repository is the **AI operating manual and toolkit** for the workflow, organized as
> Agent Skills that AI assistants can load and execute directly.
> All machine-specific paths and identities are written as placeholders — follow "Quick start"
> to configure it for any computer.

## Overview

```
+------------------------+      +-------------------------+      +-----------------------------+
| Zotero (documents)     | read | Reading / Plotting /    | write| Obsidian (the brain)        |
| Connector - WoS - CNKI | ---->| Conversion / Archiving  | ---->| Cards / Concepts / Projects |
| Topic collections      | <----| per skills in this repo | <----| index / log / conflicts     |
+------------------------+  RPC +-------------------------+ link +-----------------------------+
        ZCode Bridge ---+                 ^ LabTalk/COM             +-- ZotMoov -> Raw/PDFs (read-only)
                                     Origin plots -> PNG/PDF/TIF -> archive in 3 places
        PDF/docx/tables -- doc-to-md ---> Markdown -> AI reads (verify values in source files)
```

**Division of labor**: the human provides materials, asks questions, and sets direction; the AI does all
maintenance (literature operations, knowledge capture, plotting & archiving, format conversion).

## The five stages

| # | Stage | What it does | Sub-skill |
| --- | --- | --- | --- |
| ① | Literature management | Full read/write of Zotero items / collections / tags / attachments (ZCode Bridge RPC); multi-source acquisition (Zotero Connector / Web of Science / CNKI / OA & document delivery); intake SOP | [`skills/zotero-ops/`](skills/zotero-ops/SKILL.md) |
| ② | Knowledge capture | Obsidian vault upkeep: literature cards, concept pages, project pages; Ingest / Query / Lint / new-task flows; git commits | [`skills/vault-ops/`](skills/vault-ops/SKILL.md) |
| ③ | Scientific plotting | Origin-only plotting (origin-plot MCP) → PNG/PDF/TIF → archive in three places + embed into the experiment page | [`skills/figure-pipeline/`](skills/figure-pipeline/SKILL.md) |
| ④ | Format conversion | PDF / images / Office / spreadsheets → Markdown (always before reading) | [`skills/doc-to-md/`](skills/doc-to-md/SKILL.md) |
| ⑤ | AI middle layer | Close reading & card writing, plotting & archiving, knowledge upkeep, experience summaries — carried out by the AI through the skills above | all of this repo |

## Global red lines

1. **Numbers red line**: converted / excerpted text is for reading only; **data verification and final quoted values must be read from the original files (Excel etc.)**.
2. **Origin red line**: every scientific figure is made in Origin — never matplotlib or similar.
3. **Archiving red line**: every figure is archived in three places (project archive / `<projects>\<project>\figures\<type>\` / `<vault>\projects\<project>\attachments\`) and embedded; missing any one is not acceptable.
4. **Experience-summary red line**: every task ends with a mandatory experience summary, routed by destination (AI memory system / vault / log).
5. **git red line**: commit with `git -c user.name="<git-name>" -c user.email="<git-email>"` — **never modify the global git config**.
6. **Raw is read-only**: the raw-materials layer and all source documents are never modified; move/rename literature PDFs only through Zotero.
7. **Project drive**: new projects go on a roomy drive (e.g. `D:\Projects\`); the system drive keeps only scratch files.

## Quick start

### 1. Install as a skill

```bash
git clone https://github.com/Bigsillymao/zotero-obsidian-ai-workflow ~/.claude/skills/zotero-obsidian-ai-workflow    # Claude Code
git clone https://github.com/Bigsillymao/zotero-obsidian-ai-workflow ~/.zcode/skills/zotero-obsidian-ai-workflow     # ZCode
# or any other agent's skills directory; single sub-skills work too — copy skills/<name>/ into your skills dir
```

### 2. Configure your machine (required)

```bash
cd zotero-obsidian-ai-workflow
cp LOCAL-CONFIG.example.md LOCAL-CONFIG.md    # fill in your paths and git identity (this file never enters git)
```

Placeholders such as `<vault>`, `<projects>` and `<git-name>` across all SKILL.md files resolve from
`LOCAL-CONFIG.md`; the AI reads it before acting and asks the user when it is missing.

### 3. Check software versions

See "Version compatibility" below — Zotero / Obsidian / Origin differ substantially between versions;
confirm yours before you start.

## Version compatibility (important)

### Zotero

- **Local API and Connector require Zotero 7+**: the read-only API (`/api/users/0/...`) and the Connector
  interface exist since Zotero 7 (not in 6 and older). Enable the local API under
  Settings → Advanced → Config Editor: `extensions.zotero.httpServer.localAPI.enabled = true`.
- **ZCode Bridge** (`skills/zotero-ops/bridge/`): developed and verified on **Zotero 9.0.x**, theoretically
  compatible with Zotero 7+. Installation differs by version:
  - **Zotero 7 / 8**: normally install the XPI via "Tools → Plugins → Install Plugin From File…";
  - **Zotero 9**: regular side-loading is disabled; use `bridge/install_registry.py` (see bridge/README.md);
  - after installing, run `ping` / `selftest` before any batch operation.
- **Plugins must match your Zotero version**: ZotMoov, Better BibTeX, Jasminum, Translate — pick the
  release built for your Zotero.
- **Config locations vary by OS**: Windows `%APPDATA%\Zotero\Zotero\`; macOS `~/Library/Application Support/Zotero/`;
  Linux `~/.zotero/`. The data directory can be viewed and changed inside Zotero.

### Obsidian

- A vault is just a folder of markdown files — the core workflow is version-insensitive. Differences:
  - **Bases (`.base` files) require Obsidian 1.9+**; on older versions use the Dataview plugin instead, or
    simply delete `文献/文献库.base` — everything else keeps working;
  - graphical property editing needs 1.4+ (writing YAML frontmatter works on any version);
  - `[[wikilinks]]`, callouts and `![[embeds]]` work everywhere.
- When using the vault from several machines, mind git divergence: commit per machine, merge regularly.

### Origin

- Plotting capability follows the **origin-plot skill + origin MCP**; **versions differ significantly**:
  - the "can / cannot automate" list of this pipeline was measured on **Origin 2017 (9.4.x)**: no automated
    quit, no per-curve color/width/marker styles, no grid lines, legend box position uncontrollable,
    `save` opens a modal dialog, etc.;
  - **on Origin 2021+ some of these limits may be lifted** — verify on your own version with
    `origin_status` / `origin_doctor` instead of assuming 2017 behavior;
- without the origin-plot MCP you can still plot by hand in the Origin GUI — the "archive in three places +
  embed" part of this repo keeps working.

### MinerU (doc-to-md)

- Written against **MinerU 4.x**: subcommand-style CLI (`mineru parse <file> --tier flash|basic|standard|advanced`);
  local parsing needs `mineru server start` (once per boot);
- **3.x and earlier have a different CLI** (old global `-p/-o` flags) — check `mineru --version` and
  `mineru parse --help`; the wrapper scripts auto-detect the mineru binary (PATH → Python scripts dir →
  `MINERU_EXE` environment variable);
- models are cached under `~/.mineru/`; the default model source is modelscope. Troubleshooting (including the
  hf-xet 401 issue) is documented in the doc-to-md README.

### OS and shells

- **Windows**: all `.ps1` files here are pure ASCII — PowerShell 5.1 reads BOM-less UTF-8 scripts as ANSI/GBK
  and breaks on non-ASCII; call them as `powershell -NoProfile -ExecutionPolicy Bypass -File ...`;
- **macOS / Linux**: use `to-md.sh` for document conversion; in the CNKI scripts, `channel="msedge"` can be
  switched to `"chromium"` where Edge is unavailable;
- this repo was fully exercised on **Windows 11**; on other systems, set the paths in `LOCAL-CONFIG.md` accordingly.

### AI assistants

- The skills directory depends on your tool (Claude Code `~/.claude/skills/`, ZCode `~/.zcode/skills/`, others);
  when cloned whole, the root `SKILL.md` is the entry point and routes to the sub-skills under `skills/`.

## Dependencies

| Component | Purpose | Where to get it / version |
| --- | --- | --- |
| Zotero 7+ | Literature library | [zotero.org](https://www.zotero.org/); the bridge was verified on Zotero 9.0.x |
| Zotero plugins | ZotMoov / Jasminum / Better BibTeX / Translate | Zotero plugin ecosystem; pick releases matching your Zotero version |
| ZCode Bridge | Full Zotero read/write | `skills/zotero-ops/bridge/` in this repo (source + XPI + install script) |
| Obsidian | Knowledge base | [obsidian.md](https://obsidian.md/); the Bases view needs 1.9+ (optional) |
| origin-plot MCP + Origin | Plotting | installed separately outside this repo (e.g. `~/.zcode/skills/origin-plot`); Origin 2017+ |
| MinerU 4.x | Documents → Markdown | `pip install "mineru[core]"`; see `skills/doc-to-md/` |
| Python 3.10+ / Playwright / Edge | CNKI fetching (optional) | `pip install playwright openpyxl beautifulsoup4` |

## Repository layout

```
.
├── SKILL.md                    # root skill: setup notes + routing table + global red lines
├── README.md / README_EN.md    # this document (Chinese / English)
├── LOCAL-CONFIG.example.md     # per-machine config template (copy to LOCAL-CONFIG.md; not committed)
├── skills/
│   ├── zotero-ops/             # 1) literature: Bridge RPC / multi-source acquisition / intake & close-reading SOPs
│   │   ├── SKILL.md
│   │   ├── bridge/             #    ZCode Bridge: source + XPI + install script + compatibility notes
│   │   └── cnki/               #    CNKI batch-download scripts (de-personalized templates)
│   ├── vault-ops/              # 2) knowledge base: structure / four workflows / git conventions
│   │   ├── SKILL.md
│   │   └── templates/          #    concept / project / literature-card templates
│   ├── figure-pipeline/        # 3) plotting: Origin pipeline + three-place archiving
│   │   └── SKILL.md
│   └── doc-to-md/              # 4) conversion: PDF/Office/spreadsheets -> Markdown (end-to-end tested)
│       ├── SKILL.md
│       ├── README.md / README_EN.md
│       ├── scripts/            #    to-md.ps1 / to-md.sh / xlsx-to-md.py
│       └── tests/
└── LICENSE
```

## Verification status (snapshot at publish time)

| Component | Status |
| --- | --- |
| doc-to-md | ✅ End-to-end: PDF / docx / PNG → MD (page markers, tables preserved); xlsx / GBK CSV / HTML-masqueraded .xls / real-.xls guidance branch; Chinese and space-containing filenames |
| ZCode Bridge | ✅ Ran against a full library: collection management, batch re-filing and tagging, attachment mounting; not re-tested at publish time (Zotero was not running) |
| CNKI fetching | ✅ Tested on a campus network (captcha pass, batch downloads, metadata parsing); de-personalized before publishing, parsing logic unchanged |
| Vault workflow | In continuous use; the vault-root `CLAUDE.md` is the authoritative rulebook |
| Origin plotting | ✅ COM capability boundaries measured on Origin 2017 (list in figure-pipeline) |

Environment: Windows 11 + PowerShell 5.1 / Git Bash; Zotero 9.0.x; Origin 2017; MinerU 4.0.12.

> Honest note: the above is a snapshot at publish time. On a new machine, trust your own verification.

## A note on language

The `SKILL.md` instructions are written in Chinese — that is the working language this workflow was built in,
and AI assistants read them natively. This English README is provided so that everyone else can understand,
install and adapt the workflow.

## License

MIT — see [LICENSE](LICENSE).
