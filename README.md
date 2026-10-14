# Zotero + Obsidian + AI 科研知识工作流

> 🌐 [English](README_EN.md) | 简体中文

**一套把文献变成知识、把数据变成图、把资料变成可读文本的科研工作流。**
以 AI（Claude Code / ZCode 等助手）为中间层，Zotero 为文献入口，Obsidian 为长期知识库，
外加两条配套流水线：科研出图（Origin）与文件格式转换（→ Markdown）。

> 本仓库是这套工作流的 **AI 操作手册与工具集**，按 Agent Skill 组织，可直接被 AI 助手加载执行。
> 所有路径与身份都以占位符书写——按「快速开始」完成本机配置，即可适配任何电脑。

## 总览

```
        采集层                 AI 中间层（AI 助手）         沉淀层
┌────────────────────┐     ┌───────────────────────────┐     ┌────────────────────────┐
│ Zotero（入口）     │ 读取 │ 精读 / 出图 / 转换 / 归档 │ 写入 │ Obsidian vault（大脑） │
│ Connector·WoS·知网 │ ───→│ 按本仓库各子技能执行      │ ───→│ 卡片·概念·项目·问答    │
│ 主题 collections   │ ←───│                           │ ←───│ index·log·矛盾清单     │
└────────────────────┘  RPC └───────────────────────────┘ 回链 └────────────────────────┘
        ZCode Bridge ──┘                ↑ LabTalk/COM                └─ ZotMoov → Raw/文献PDF（只读）
                                    出图（择优）─→ PNG/PDF/TIF ─→ 三处归档
        PDF/docx/表格 ── doc-to-md ───→ Markdown ──→ AI 阅读（数值核校仍以原始文件为准）
```

**分工**：用户提供资料、提问、把关方向；AI 负责一切维护（文献操作、知识沉淀、出图归档、格式转换）。

## 五个环节

| # | 环节 | 做什么 | 子技能 |
| --- | --- | --- | --- |
| ① | 文献管理 | Zotero 条目/分类/标签/附件全量读写（ZCode Bridge RPC）；多源文献获取（Zotero Connector / Web of Science / 知网 / OA 与文献传递）；入库 SOP | [`skills/zotero-ops/`](skills/zotero-ops/SKILL.md) |
| ② | 知识沉淀 | Obsidian vault 维护：文献卡片/概念页/项目页；Ingest / Query / Lint / 新任务；git 提交 | [`skills/vault-ops/`](skills/vault-ops/SKILL.md) |
| ③ | 科研出图 | 择优出图（Origin：origin-plot MCP / 模板路线；或 Python 绘图库）→ PNG/PDF/TIF → 三处归档 + 试验页嵌入 | [`skills/figure-pipeline/`](skills/figure-pipeline/SKILL.md) |
| ④ | 格式转换 | PDF / 图片 / Office / 表格 → Markdown（读文档前必做） | [`skills/doc-to-md/`](skills/doc-to-md/SKILL.md) |
| ⑤ | AI 中间层 | 精读写卡、出图归档、知识维护、经验总结——由 AI 按上述技能执行 | 本仓库全部 |

## 全局红线

1. **数值红线**：转换 / 摘录出的文本只用于阅读；**数据校核、定案值引用必须回原始文件（Excel 等）读精确值**。
2. **绘图工具**：不再强制 Origin（2026-10-14 变更）——按“好用 + 出图质量”择优（Origin / Python 绘图库 / 其他均可）。
3. **归档红线**：每次出图三处归档（资料包原位 / `<项目目录>\<项目>\图\<类型>\` / `<vault>\项目\<项目>\附件\`）+ 嵌入 + git，缺一不可。
4. **经验总结红线**：每个任务收尾必须做经验总结，按去向分流（AI 记忆 / vault / log）。
5. **git 红线**：提交用 `git -c user.name="<git-name>" -c user.email="<git-email>"`，**不改动全局 git 配置**。
6. **Raw 只读**：原始资料层绝不修改；文献 PDF 的移动/重命名一律走 Zotero。
7. **项目盘**：新项目放空间充裕的盘（如 `D:\Projects\`），系统盘只放临时文件。

## 快速开始

### 1. 安装为技能

```bash
git clone https://github.com/Bigsillymao/zotero-obsidian-ai-workflow ~/.claude/skills/zotero-obsidian-ai-workflow    # Claude Code
git clone https://github.com/Bigsillymao/zotero-obsidian-ai-workflow ~/.zcode/skills/zotero-obsidian-ai-workflow     # ZCode
# 或其他 AI 工具的 skills 目录；也可只用单个子技能：把 skills/<名>/ 复制进 skills 目录
```

### 2. 完成本机配置（必须）

```bash
cd zotero-obsidian-ai-workflow
cp LOCAL-CONFIG.example.md LOCAL-CONFIG.md    # 填好你的路径与 git 身份（该文件不进 git）
```

各 SKILL.md 里的 `<vault>`、`<项目目录>`、`<git-name>` 等占位符，取值一律以 `LOCAL-CONFIG.md` 为准；
AI 助手使用前先读它，缺失时主动询问用户。

### 3. 检查软件版本

见下面「版本差异与兼容」——不同版本的 Zotero / Obsidian / Origin 可用功能不同，先确认再动手。

## 版本差异与兼容（重要）

### Zotero

- **本地 API 与 Connector 需 Zotero 7+**：只读 API（`/api/users/0/...`）与 Connector 接口自 Zotero 7 起提供（6 及以下没有）。启用只读 API：设置 → 高级 → 配置编辑器，`extensions.zotero.httpServer.localAPI.enabled = true`。
- **ZCode Bridge**（`skills/zotero-ops/bridge/`）：在 **Zotero 9.0.x** 上开发并实测通过，Zotero 7+ 理论兼容。安装方式因版本而异：
  - **Zotero 7 / 8**：一般可直接「工具 → 插件 → Install Plugin From File…」常规安装 XPI；
  - **Zotero 9**：实测常规侧载扫描失效，需用 `bridge/install_registry.py` 注册表注入（详见 bridge/README.md）；
  - 装好后先 `ping` / `selftest` 验证，再做批量操作。
- **插件要匹配 Zotero 版本**：ZotMoov、Better BibTeX、Jasminum、Translate 都要选对应你 Zotero 版本的发行版。
- **配置位置因系统而异**：Windows `%APPDATA%\Zotero\Zotero\`；macOS `~/Library/Application Support/Zotero/`；Linux `~/.zotero/`。数据目录可在 Zotero 内查看与更改。

### Obsidian

- vault 只是 md 文件集合，核心工作流对版本不敏感；差异点在：
  - **Bases（`.base` 文件）需要 Obsidian 1.9+**；旧版本请改用 Dataview 插件，或直接删掉 `文献/文献库.base`，其余功能不受影响；
  - 属性（properties）的图形化编辑需 1.4+（写入 YAML frontmatter 本身不受版本限制）；
  - `[[wikilink]]`、callout、`![[嵌入]]` 各版本通用。
- 多端使用（如桌面 + 笔记本）时注意 git 分叉：每端各自提交、定期合并。

### Origin

- 出图能力以 **origin-plot 技能 + origin MCP** 为准；**版本差异明显**：
  - 本流水线的「能/不能脚本化」清单实测于 **Origin 2017（9.4.x）**：不能自动退出、不能设逐曲线颜色/线宽/标记形状、不能加网格线、图例框位置不可控、`save` 会弹模态框等；
  - **2021 及更新版本上部分限制可能已解除**——请在你自己版本上用 `origin_status` / `origin_doctor` 实测，不要照搬 2017 的结论；
- 未安装 origin-plot MCP 时：可先在 Origin GUI 手工出图，本仓库的「三处归档 + 嵌入」流程照常可用。

### MinerU（doc-to-md）

- 按 **MinerU 4.x** 编写：子命令式 CLI（`mineru parse <文件> --tier flash|basic|standard|advanced`），本地解析需先 `mineru server start`（每次开机一次）；
- **3.x 及更早版本 CLI 与参数不同**（如旧版 `-p/-o` 全局参数），请以 `mineru --version` 与 `mineru parse --help` 为准；脚本自动探测 mineru 位置（PATH → Python scripts 目录 → `MINERU_EXE` 环境变量）；
- 模型缓存在 `~/.mineru/`；模型源默认 modelscope，排障（含 hf-xet 401）见 doc-to-md 的 README。

### 操作系统与 Shell

- **Windows**：仓库内 `.ps1` 均为纯 ASCII——PowerShell 5.1 会把无 BOM 的 UTF-8 脚本当 ANSI/GBK 读；建议 `powershell -NoProfile -ExecutionPolicy Bypass -File ...` 调用；
- **macOS / Linux**：文档转换用 `to-md.sh`；知网抓取脚本里 `channel="msedge"` 可改为 `"chromium"`（无 Edge 的环境）；
- 本仓库在 **Windows 11** 上完整跑通；其他系统按各自路径在 `LOCAL-CONFIG.md` 里配置。

### AI 助手

- 技能目录因工具而异（Claude Code `~/.claude/skills/`、ZCode `~/.zcode/skills/` 等）；整体克隆时根 `SKILL.md` 是入口，按路由表读取 `skills/` 下的子技能。

## 依赖

| 组件 | 用途 | 获取 / 版本要求 |
| --- | --- | --- |
| Zotero 7+ | 文献库 | [zotero.org](https://www.zotero.org/)；本桥实测于 Zotero 9.0.x |
| Zotero 插件 | ZotMoov / Jasminum / Better BibTeX / Translate | Zotero 插件市场；选匹配你 Zotero 版本的发行版 |
| ZCode Bridge | Zotero 全量读写 | 本仓库 `skills/zotero-ops/bridge/`（源码 + XPI + 安装脚本） |
| Obsidian | 知识库 | [obsidian.md](https://obsidian.md/)；Bases 视图需 1.9+（可选） |
| origin-plot MCP + Origin | 出图 | 本仓库外单独安装（`~/.zcode/skills/origin-plot` 或等价位置）；Origin 2017+ |
| MinerU 4.x | 文档 → Markdown | `pip install "mineru[core]"`；详见 `skills/doc-to-md/` |
| Python 3.10+ / Playwright / Edge | 知网抓取（可选） | `pip install playwright openpyxl beautifulsoup4` |

## 仓库结构

```
.
├── SKILL.md                    # 总入口技能：配置说明 + 路由表 + 全局红线
├── README.md                   # 本文件（含版本差异与兼容）
├── LOCAL-CONFIG.example.md     # 本机配置模板（复制为 LOCAL-CONFIG.md 后填写，不进 git）
├── skills/
│   ├── zotero-ops/             # ① 文献：Bridge RPC / 多源文献获取 / 入库与精读 SOP
│   │   ├── SKILL.md
│   │   ├── bridge/             #    ZCode Bridge：源码 + XPI + 安装脚本 + 兼容坑
│   │   └── cnki/               #    知网批量下载脚本（去个人化模板）
│   ├── vault-ops/              # ② 知识库：结构 / 四类工作流 / git 规范
│   │   ├── SKILL.md
│   │   └── templates/          #    概念页 / 项目页 / 文献卡片模板
│   ├── figure-pipeline/        # ③ 出图：Origin 流水线 + 三处归档
│   │   └── SKILL.md
│   └── doc-to-md/              # ④ 格式转换：PDF/Office/表格 → Markdown（已端到端实测）
│       ├── SKILL.md
│       ├── README.md
│       ├── scripts/            #    to-md.ps1 / to-md.sh / xlsx-to-md.py
│       └── tests/
└── LICENSE
```

## 实测与环境（发布时快照）

| 组件 | 验证状态 |
| --- | --- |
| doc-to-md | ✅ 端到端实测：PDF / docx / PNG → MD（页标记、表格保留）；xlsx / GBK-csv / HTML 伪装 .xls / 真 .xls 引导分支；中文与空格文件名 |
| ZCode Bridge | ✅ 在完整文献库上走通：分类管理、批量归位与标签、附件挂载；发布前未复测（Zotero 未运行） |
| 知网抓取 | ✅ 校园网环境实测（安全验证通过、批量下载、题录解析）；发布前做了去个人化改写，解析逻辑未改动 |
| vault 工作流 | 持续使用中；规则以 vault 根 `CLAUDE.md` 为权威 |
| Origin 出图 | ✅ COM 能力边界实测于 Origin 2017（清单见 figure-pipeline） |

环境：Windows 11 + PowerShell 5.1 / Git Bash；Zotero 9.0.x；Origin 2017；MinerU 4.0.12。

> 诚实声明：以上为发布时的实况快照；换到新环境后，以新环境的实测结果为准。

## License

MIT — see [LICENSE](LICENSE).
