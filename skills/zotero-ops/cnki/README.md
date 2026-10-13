# CNKI 批量下载脚本（模板）

从知网批量检索并下载文献（校园网 / 机构访问 + 有头浏览器 + 持久 profile 条件下可用）。
本目录脚本来自一套已实测的自动化，**发布前做了去个人化改写：路径全部改走环境变量，目标文献清单换成示例，检索/解析/下载逻辑未改动**。请按你的环境改好再运行。

## 依赖

- Python + playwright（`pip install playwright`）；浏览器用系统 Edge（`channel="msedge"`），无 Edge 的环境改为 `"chromium"`
- 一个**持久化浏览器 profile 目录**（保存登录态与安全验证 Cookie，勿删）——通过环境变量 `CNKI_PROFILE` 指定

## 运行

```bash
export PYTHONIOENCODING=utf-8
export CNKI_PROFILE="/你的/持久profile目录"     # 也可直接改脚本里的默认值
export CNKI_OUTDIR="/你的/下载目录"
python zz_fetch_cnki.py      # 按标题批量检索+下载（先把脚本里的 PAPERS 示例清单改成你的文献）
python zz_cnki_solver.py     # 备用：安全验证滑块自动求解（先设 CNKI_KW）
```

## 关键经验（与 Zotero 无关，纯知网）

1. **安全验证**：无头浏览器必弹；有头 + 持久 profile + `--disable-blink-features=AutomationControlled` 可通过（首次可能弹滑块，重启/等待后可能自动放行；滑块为拼图对齐型，求解器用零均值归一化互相关找缺口）
2. **检索 URL**：`https://kns.cnki.net/kns8s/defaultresult/index?kw=<关键词URL编码>&korder=TI`（标题检索；作者用 `AU`）
3. **下载**：打开详情页 → 点「PDF下载」（回退「CAJ下载」）→ 用 Playwright download 事件捕获保存
   - ⚠ 捕获时**记录点击前的捕获列表长度，再等新增**，否则会拿到上一步残留的下载事件（曾有把别的来源 PDF 存成另一篇文献的教训）
4. **题录**：详情页 `document.body.innerText` 含 导师/DOI/学位授予单位/期刊卷期 等，可直接解析
5. 学位论文通常提供 PDF；老刊无 DOI 属正常

## 适用边界

仅用于你有合法访问权的文献（校园网 / 机构订阅 / 开放获取），下载后遵守出版商与所在机构的使用规定。
