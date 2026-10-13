---
name: zotero-ops
description: 操作 Zotero 文献库与多源文献获取的全部方法：ZCode Bridge RPC（新建/修改/删除条目、分类、标签、挂附件）、多源文献获取（Zotero Connector / Web of Science 导出导入 / 知网 CNKI 批量下载 / OA 与文献传递）、ZotMoov 附件搬迁、文献入库与精读 SOP。当用户要求导入/整理 Zotero、挂附件、改分类标签、从知网或 Web of Science 等来源获取文献、精读论文写卡片时使用。
---

# Zotero 操作（文献入口）

## 环境与配置

- 各项路径的取值见 **`LOCAL-CONFIG.md`**：`<zotero-exe>`（程序位置）、`<zotero-data>`（数据目录）、`<bridge-url>`（默认 `http://127.0.0.1:23119`）
- 默认位置参考：Windows 程序 `C:\Program Files\Zotero`、数据目录 `%USERPROFILE%\Zotero`；macOS `/Applications/Zotero.app`、`~/Zotero`；Linux 视安装方式
- 启动/关闭：没开先启动 Zotero；Windows 下关闭用 `taskkill /F`（不带 `/F` 关不掉）
- 分类建议**按主题**不按项目（跨项目可续用），如 `理论机理 / 试验方法 / 应用案例 …`，名称自定

## 版本差异（Zotero）

- **本地只读 API 与 Connector 需 Zotero 7+**（6 及以下没有）；启用本地 API：设置 → 高级 → 配置编辑器，`extensions.zotero.httpServer.localAPI.enabled = true`
- **ZCode Bridge 实测于 Zotero 9.0.x，Zotero 7+ 理论兼容**；安装方式因版本而异：
  - Zotero 7 / 8：一般可直接「工具 → 插件 → Install Plugin From File…」常规装 XPI；
  - Zotero 9：常规侧载扫描失效，需 `bridge/install_registry.py` 注册表注入（见 `bridge/README.md`）
- 插件（ZotMoov / Better BibTeX / Jasminum / Translate）必须选**匹配你 Zotero 版本**的发行版
- 桥接装好后先 `ping` / `selftest` 验证，再用于批量操作

## 全量读写的唯一通道：ZCode Bridge

本地插件 `zcode-bridge@zcode.local`（源码与重装说明在 `bridge/`；Zotero 9 兼容坑 7 条见其 README）。

- 端点：`POST <bridge-url>/zcode/rpc`，body 为操作对象 `{"op": "...", ...}`；`GET <bridge-url>/zcode/ping` 探活
- op 目录：`ping` `selftest` `items.list` `item.create` `item.update`（fields / tagsAdd / tagsRemove / creators）`item.delete`（erase）`item.setCollections`（replace/add/remove）`collections.list` `collection.create` `collection.update`（parentKey=null 拉平）`attachment.importFile`（imported_file / linked_file）`zotero.eval`（受 pref 开关控制）
- Python 调用样例（端口以 `LOCAL-CONFIG.md` 为准，Zotero 设置里可改）：

```python
import json, urllib.request

BASE = "http://127.0.0.1:23119"

def zot(op, **kw):
    body = json.dumps({"op": op, **kw}).encode("utf-8")
    req = urllib.request.Request(BASE + "/zcode/rpc", data=body,
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())

print(zot("ping"))
print(zot("collections.list"))                       # 先取分类 key，避免写错
zot("item.setCollections", key="<itemKey>", collections=["<collectionKey>"], mode="add")
zot("attachment.importFile", parentKey="<itemKey>",
    path=r"<文献落盘>\论文文件名.pdf", linkMode="linked_file")
```

- 只读备用通道：本地 API `<bridge-url>/api/users/0/...`（POST 被拒）
- ⚠ 连接器 `/connector/saveItems`：只能新建、且存到 **Zotero UI 当前选中分类**（不可控），已被 Bridge 取代
- 操作纪律：改动前先 `items.list` / `collections.list` 核对 key；附件挂载前确认文件在磁盘、parentKey 正确

## 文献获取（多来源）

**通则**：能用 Zotero Connector 保存的就用 Connector（浏览器扩展；支持 **Web of Science**、期刊官网、PubMed、arXiv、Google Scholar 等绝大多数站点，自动存题录、订阅范围内自动带 PDF）；站点不支持 Connector 或要批量时，走「站点导出 → Zotero 导入」。拿到 PDF 后统一走下面的入库 SOP。

### Web of Science 等外文库（导出-导入）

1. 机构订阅环境（校园网 / VPN）检索 → 勾选记录 → 加入 **Marked List**
2. Marked List → Export → 选 **RIS** 或 **BibTeX**（记录多时分批导出）
3. Zotero 导入该文件（可把文件直接拖到目标 collection 上导入）；重复条目按 DOI 提示处理
4. 少量单篇：在 WoS 记录页直接点 Zotero Connector 图标保存
5. 全文：记录页 Full Text Links / 出版页（订阅范围内）；拿不到走下面「OA 与文献传递」

（如需批量自动化抓取 WoS，可按 `cnki/` 的模式另建 Playwright 脚本，或走校内 WoS API——两者都需要机构权限）

### 知网（CNKI）批量下载（`cnki/`）

- 前提：校园网 IP（或机构访问）+ 有头 Edge + 持久 profile `<cnki-profile>`（保存登录态与验证 Cookie，**勿删**）；无 Edge 的环境把脚本里 `channel="msedge"` 改为 `"chromium"`
- 脚本：`zz_fetch_cnki.py`（按标题批量检索下载）、`zz_cnki_solver.py`（安全验证滑块备用求解器）；用法与坑见 `cnki/README.md`
- 检索 URL：`https://kns.cnki.net/kns8s/defaultresult/index?kw=<URL编码>&korder=TI`（作者检索用 `AU`）
- 关键经验：无头浏览器必弹安全验证，有头 + 持久 profile 可过；下载用 Playwright download 事件捕获，**记录点击前捕获列表长度再等新增**（防串台）；详情页 `innerText` 可直接解析题录（导师/DOI/卷期）

### OA 与文献传递（拿全文的合法途径）

- OA 通道：Unpaywall（浏览器扩展）、PubMed Central、arXiv、DOAJ、机构知识库、作者主页（注意：部分机构库只有题录、没有全文）
- 无订阅期刊：图书馆文献传递 / 馆际互借；建议打个跟踪标签（如 `待文献传递`）持续跟进

## 文献三条 SOP（与 vault 联动）

1. **入库**：任意来源（知网 / Web of Science / 期刊页 / 学术检索……）→ Zotero Connector 保存或导出文件导入（中文元数据靠茉莉花等插件）→ PDF 由 ZotMoov 移入 `<vault>/Raw/文献PDF/` 并转链接式附件 → 拖入主题 collection；入库时只手打「特点」粗标
2. **精读**：用户说"精读 xxx" → 先用 `doc-to-md` 把 PDF 转 Markdown 读全文 → 按 `../vault-ops/templates/文献卡片模板.md` 写卡片入 `<vault>/文献/` → 四维标签由 AI 判断填入、用户复核 → 与课题页/概念页互链 → git 提交
3. **引用**：Word 里使用 Zotero 插件插引用（样式按目标期刊/学校规范，如 GB/T 7714）；vault 卡片是论证素材，正式引用以 Zotero 条目为准

**四维标签框架**（下表为示例取值，**按你的学科改写**；改后同步到 vault 与 Zotero 标签）：

| 维度 | 取值（示例） |
| --- | --- |
| 作用 | `假说支撑` `反例质疑` `方法借鉴` `对照数据` `背景综述` `规范依据` `表述借鉴` |
| 特点 | `试验研究` `综述` `理论机理` `数值模拟` `工程案例` `标准规范` |
| 方法 | `<你的学科方法词，可多个>`（如 方法A / 方法B / 方法C） |
| 结论方向 | `支持` `反对` `中性` |

状态标签可按需自定，如 `PDF已归档` / `缺PDF` / `待下载` / `待文献传递`（跟踪无订阅全文）。
