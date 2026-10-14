---
name: research-workflow
description: 科研知识工作流总入口（Zotero + Obsidian + AI 中间层）：多源文献获取与精读、Obsidian 知识库维护（ingest/query/lint/体检）、科研出图（Origin）与三处归档、文档/表格/PDF 转 Markdown。当要处理文献、维护或查询知识库、出图或归档图件、读 PDF/文档/表格、任务收尾做经验总结时使用。Entry point for a Zotero + Obsidian + AI research knowledge workflow.
---

# 科研知识工作流（Zotero + Obsidian + AI）

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

分工：用户提供资料、提问、把关方向；AI 负责一切维护。**本仓库就是 AI 的操作手册。**

## 首次使用：先完成本机配置

1. 把 `LOCAL-CONFIG.example.md` 复制为 `LOCAL-CONFIG.md`，与用户一起填好各项（该文件不进 git）
2. 本仓库所有 `<vault>`、`<项目目录>`、`<git-name>`、`<cnki-profile>` 等占位符的取值，一律来自 `LOCAL-CONFIG.md`；**AI 使用前先读它，缺失时主动询问用户**
3. 检查各软件版本，按 `README.md`「版本差异与兼容」与各子技能的「版本差异」节适配——Zotero 7/9、Obsidian 版本、Origin 2017 与 2021+ 的能力边界都不同

## 子技能路由（按任务进入对应 SKILL.md）

| 任务 | 进入 |
| --- | --- |
| Zotero 条目/分类/附件操作、多源文献获取（WoS / 知网 / OA 与文献传递）、文献入库与精读 | [`skills/zotero-ops/SKILL.md`](skills/zotero-ops/SKILL.md) |
| Obsidian 知识库维护（Ingest/Query/Lint/新任务、页面与 git 规范） | [`skills/vault-ops/SKILL.md`](skills/vault-ops/SKILL.md) |
| 科研出图（Origin）与图件三处归档 | [`skills/figure-pipeline/SKILL.md`](skills/figure-pipeline/SKILL.md) |
| PDF/图片/Office/表格 → Markdown（读文档前必做） | [`skills/doc-to-md/SKILL.md`](skills/doc-to-md/SKILL.md) |

路径相对本技能目录；也可把任一子目录单独装进 AI 的 skills 目录独立使用。

## 全局红线（每次任务都适用）

1. **数值红线**：转换 / 摘录出的文本只用于阅读；**数据校核、定案值引用必须回原始文件（Excel 等）读精确值**。
2. **绘图工具**：不再强制 Origin（2026-10-14 变更）——按“好用 + 出图质量”择优（Origin / Python 绘图库 / 其他均可）。
3. **归档红线**：每次出图必须三处归档——资料包原位 + `<项目目录>\<项目>\图\<类型>\` + `<vault>\项目\<项目>\附件\`，并在试验页嵌入；同步 index/log + git。缺一不可。
4. **经验总结红线**：每个任务收尾必须做经验总结（有效做法 / 踩坑与修复 / 迁移提示），按去向分流：工具·网络·自动化坑 → AI 记忆系统；领域知识与方法论 → vault；两条都追加 `log.md`。
5. **git 红线**：知识库提交用 `git -c user.name="<git-name>" -c user.email="<git-email>" commit`（取值见 LOCAL-CONFIG），**不改动全局 git 配置**——每台机器既有的协作身份不受影响。
6. **Raw 只读**：`Raw/` 层与一切原始资料绝不修改；文献 PDF 的移动/重命名一律走 Zotero（不手动）。
7. **项目盘**：新项目放空间充裕的盘（如 `D:\Projects\`），系统盘只放临时脚本与小文件。

## 版本差异总览

关键差异与完整说明见 `README.md`「版本差异与兼容」；各子技能内另有「版本差异」节：

- **Zotero**：本地 API / Connector 需 7+；Bridge 实测于 9.0.x（7+ 理论兼容），7/8 与 9 的插件安装方式不同
- **Obsidian**：Bases（`.base`）需 1.9+，旧版用 Dataview 或纯表格替代
- **Origin**：能力边界随版本不同——2017 不能脚本化的功能在 2021+ 部分可用，以本机实测为准
- **MinerU**：本仓库按 4.x 子命令式 CLI 编写（`mineru parse ...`）
