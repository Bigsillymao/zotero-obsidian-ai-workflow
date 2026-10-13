# LOCAL-CONFIG —— 本机配置示例

> **用法**：把本文件复制为 `LOCAL-CONFIG.md`，与 AI 助手一起填好你的实际值。
> `LOCAL-CONFIG.md` 已被 `.gitignore` 排除，**不会进 git**。
> AI 助手使用本仓库时：**先读 `LOCAL-CONFIG.md`** 决定各项取值；若不存在，主动询问用户并按本表创建。
> 各 SKILL.md 中的 `<vault>`、`<项目目录>`、`<git-name>` 等占位符，取值一律以该文件为准。

| 键 | 说明 | 示例 / 默认 |
| --- | --- | --- |
| `vault` | Obsidian 知识库路径（建议放在 git 仓库里） | Windows `D:\Vault`；macOS/Linux `~/Vault` |
| `项目目录` | 放「项目文件夹」的位置（图件归档②的根；桌面也可换成任意目录） | `%USERPROFILE%\Desktop` 或自定 |
| `资料包根` | 各项目资料主副本的公共根目录（图件归档①） | 自定，如 `D:\Research` |
| `zotero-exe` | Zotero 可执行程序位置 | Windows `C:\Program Files\Zotero`；macOS `/Applications/Zotero.app`；Linux 视安装方式 |
| `zotero-data` | Zotero 数据目录（Zotero 设置 → 高级 → 文件和文件夹 里可查看/更改） | `%USERPROFILE%\Zotero` / `~/Zotero` |
| `zotero-profile` | Zotero 配置目录（装桥接插件、查 prefs 用） | Windows `%APPDATA%\Zotero\Zotero\Profiles\<随机后缀>.default` |
| `bridge-url` | 本桥 HTTP 端点（端口 = Zotero 的 httpServer 端口） | `http://127.0.0.1:23119` |
| `文献落盘` | ZotMoov 的 PDF 目标目录（建议指向 `Raw/文献PDF`） | `<vault>/Raw/文献PDF` |
| `下载目录` | 新文献/文件默认落盘处 | `%USERPROFILE%\Downloads` |
| `cnki-profile` | 知网抓取用的持久浏览器 profile 目录（保存登录态与验证 Cookie） | 自定，如 `~/.cnki-browser-profile`（勿删） |
| `git-name` / `git-email` | 知识库 git 提交身份（用 `-c` 内联传入，**不改动全局 git 配置**） | 如 `YourName` / `you@example.com` |
| `origin-版本` | Origin 版本号（AI 据此判断 COM 能力边界） | 如 `2017` / `2021` / `2024` |
| `mineru` | MinerU 可执行路径（留空 = 脚本自动探测 PATH） | 空 或 `mineru` |
