# ZCode Bridge — Zotero 本地操作桥

给本机 Zotero 插件体系加的一个小型 HTTP 桥，让 AI 代理（ZCode 等）可以**完整操作 Zotero 文库**
（新建/修改/删除条目、分类归属、标签、挂本地文件为附件）。

- 开发者/来源：由 AI 助手开发，用于「参考文献录入与整理」类任务。
- 性质：本地插件（zcode-bridge@zcode.local，v0.1.0），**仅监听 127.0.0.1**（Zotero 内置 HTTP 服务器）。
- 兼容：**Zotero 9.x 实测通过**（Zotero 7+ 理论兼容）。注意安装方式：
  - **Zotero 7 / 8**：一般可直接「工具 → 插件 → Install Plugin From File…」常规安装 XPI；
  - **Zotero 9**：常规侧载扫描失效，需用 `install_registry.py` 注册表注入（见下文「维护」）。

## 端点

| 端点 | 方法 | 说明 |
|---|---|---|
| `/zcode/ping` | GET/POST | 探活 |
| `/zcode/rpc` | POST | JSON body：`{"op": "<操作>", ...参数}`（Zotero 9 中 body 已是对象） |

## 支持的操作（op）

| op | 参数 | 说明 |
|---|---|---|
| `ping` | — | 返回版本信息 |
| `selftest` | — | 自检：建 1 条再删除 |
| `items.list` | — | 全部条目（key/类型/标题/父级/分类key/标签） |
| `item.create` | itemType, fields{}, creators[], tags[], collections[keys] | 新建条目并可指定分类 |
| `item.update` | key, fields{}, tagsAdd[], tagsRemove[], creators[] | 改字段/标签/作者 |
| `item.delete` | key, erase(bool) | erase=true 永久删除；否则回收站 |
| `item.setCollections` | key, collections[keys], mode(replace/add/remove) | 分类归属 |
| `collections.list` | — | 所有分类（DB 直查，含嵌套层级） |
| `collection.create` | name, parentKey? | 新建分类 |
| `collection.update` | key, name?, parentKey(null=拉平) | 改名/改父级 |
| `attachment.importFile` | parentKey, path, linkMode(imported_file/linked_file) | 挂本地文件 |
| `zotero.eval` | code | 在 Zotero 内执行 JS（需 pref，见下） |

## 维护

- 日志：系统临时目录下的 `zcode-bridge.log`（想换位置改 `src/bootstrap.js` 顶部），随时可删。
- **重装/升级**：关闭 Zotero → 重建 XPI → 把 `zcode-bridge.xpi` 复制为
  `<Zotero Profile>\extensions\zcode-bridge@zcode.local.xpi` → 运行 `install_registry.py`（写注册表+清缓存）→ 启动 Zotero。
- **卸载**：Zotero → 工具 → 插件 → 找到 ZCode Bridge → 移除；或关闭 Zotero 后删
  `<Profile>\extensions\zcode-bridge@zcode.local.xpi` 并从 `extensions.json` 去掉对应条目（Zotero 启动时会自愈）。
- **关闭 eval 后门**：把 pref `extensions.zcode-bridge.allowEval` 设为 false（默认安装时已设 true）。
- 模块结构：`src/manifest.json` + `src/bootstrap.js`（全部逻辑，含全部 ops 与端点注册）。

## 安全边界（必读）

- 仅本机回环可访问；但其能力 = 本机任何程序都能操作你的文库（与 Zotero 连接器同类，但更强）。
- `zotero.eval` 可在 Zotero 内执行任意 JS——这是"完全操作"的最终后门，已用 pref 开关控制。
- 不需要时建议禁用/移除（见上"卸载"）。

## Zotero 9 兼容踩坑（供后续维护）

1. 插件沙箱中 `Zotero` 是全局对象；`Components.classes["@zotero.org/Zotero;1"]` 已废除。
2. `Zotero.Prefs.get(name)` 默认读 `extensions.zotero.*` 分支；读自定义 pref 要 `get(name, true)`。
3. 取值器异步化：`Items.getAll`、`getByLibraryAndKey` 等需 `await`（优先 `*Async` 变体）。
4. `Collections.getByLibrary` 只返回顶层 → 全量分类请查 DB（`collections` 表）。
5. Connector 的 `/connector/saveItems` 只能新建且存到 **UI 当前选中分类**（不可控目标）。
6. 侧载扫描失效：安装=注册表注入（克隆现役插件条目 + 删 `addonStartup.json.lz4` + manifest 必须带 `update_url`）。
7. `taskkill` 不带 `/F` 关不掉 Zotero，重启须 `taskkill /F`。
