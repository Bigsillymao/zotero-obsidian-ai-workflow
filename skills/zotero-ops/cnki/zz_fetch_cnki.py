# -*- coding: utf-8 -*-
"""知网批量下载（模板）：检索 → 命中结果行 → 详情页 → 抓题录 → 点下载（PDF 优先，回退 CAJ）→ 存到下载目录。

- 路径全部走环境变量（见下）；PAPERS 为示例清单，改成你的文献即可；
- 检索 / 解析 / 下载逻辑取自一套已实测版本，未改动。
环境变量：
  CNKI_PROFILE  持久浏览器 profile 目录（保存登录态与验证 Cookie；默认 ~/.cnki-browser-profile）
  CNKI_OUTDIR   下载保存目录（默认 ~/Downloads）
  CNKI_RESULT   结果 JSON 路径（默认 <系统临时目录>/cnki_fetch_results.json）
"""
import json, time, urllib.parse, os, tempfile
from playwright.sync_api import sync_playwright

UD = os.environ.get("CNKI_PROFILE") or os.path.expanduser("~/.cnki-browser-profile")
DOC = os.environ.get("CNKI_OUTDIR") or os.path.expanduser("~/Downloads")
RESULT_JSON = os.environ.get("CNKI_RESULT") or os.path.join(tempfile.gettempdir(), "cnki_fetch_results.json")

# 示例清单：kw=标题关键词（整串作标题检索）；author=作者（核对命中用）；kind=thesis/journal（仅记录）；save=保存文件名（不含扩展名）
PAPERS = [
    {"kw": "<你的目标文献标题 1>", "author": "<作者>", "kind": "journal", "save": "标题1_作者"},
    {"kw": "<你的目标文献标题 2>", "author": "<作者>", "kind": "thesis", "save": "标题2_作者"},
]

os.makedirs(DOC, exist_ok=True)
results = []
if os.path.exists(RESULT_JSON):
    try: results = json.load(open(RESULT_JSON, encoding="utf-8"))
    except Exception: results = []

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        UD, headless=False, channel="msedge", locale="zh-CN",
        viewport={"width": 1400, "height": 900}, accept_downloads=True,
        args=["--disable-blink-features=AutomationControlled"],
    )
    collected = []
    ctx.on("page", lambda pg_: pg_.on("download", lambda d: collected.append(d)))
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.on("download", lambda d: collected.append(d))

    for item in PAPERS:
        rec = {"kw": item["kw"], "author": item["author"], "kind": item["kind"], "status": "pending"}
        print("\n===== " + item["kw"][:40] + " =====")
        try:
            url = "https://kns.cnki.net/kns8s/defaultresult/index?kw=" + urllib.parse.quote(item["kw"]) + "&korder=TI"
            pg.goto(url, timeout=90000, wait_until="domcontentloaded")
            pg.wait_for_timeout(7000)
            if "安全验证" in pg.title():
                print("  !! 又出验证页，跳过")
                rec["status"] = "verify_blocked"
                results.append(rec); continue

            # 找目标结果行
            links = pg.evaluate("""(kw) => {
              const out = [];
              document.querySelectorAll('a').forEach(a => {
                const t = (a.innerText || '').trim();
                const h = a.href || '';
                if (h.includes('kcms2/article/abstract') && t.length > 6) out.push({t, h});
              });
              return out;
            }""", item["kw"])
            target = None
            for l in links:
                if l["t"].replace(" ", "")[:14] in item["kw"] or item["kw"][:14] in l["t"]:
                    target = l; break
            if not target and links:
                print("  未精确命中，候选:", [l["t"][:40] for l in links[:5]])
                target = links[0]
            if not target:
                print("  !! 无结果链接")
                rec["status"] = "no_result"
                results.append(rec); continue
            print("  命中:", target["t"][:50])
            rec["cnki_title"] = target["t"]
            rec["detail_url"] = target["h"]

            # 打开详情页
            pg.goto(target["h"], timeout=90000, wait_until="domcontentloaded")
            pg.wait_for_timeout(6000)
            info = pg.evaluate("""() => {
              const txt = document.body.innerText.slice(0, 2600);
              const btns = Array.from(document.querySelectorAll('a,button')).map(b => (b.innerText||'').trim()).filter(x => x && x.length < 16 && /下载|PDF|CAJ|收藏|订阅/.test(x));
              return {txt, btns: [...new Set(btns)]};
            }""")
            rec["detail_text"] = info["txt"]
            rec["buttons"] = info["btns"]
            print("  按钮:", info["btns"])

            # 点击下载（PDF 优先）；防串台：记录点击前捕获长度，等新增
            got = False
            for prefer in ["PDF下载", "下载PDF", "PDF", "CAJ下载", "整本下载", "下载"]:
                if any(prefer == b or prefer in b for b in info["btns"]):
                    n0 = len(collected)
                    try:
                        el = pg.locator("a,button", has_text=prefer).first
                        el.scroll_into_view_if_needed(timeout=8000)
                        el.click(timeout=8000)
                    except Exception as e:
                        print("  点击失败(" + prefer + "):", str(e)[:80])
                        continue
                    # 等下载（只认点击后新增的事件）
                    t0 = time.time()
                    while time.time() - t0 < 75:
                        if len(collected) > n0:
                            break
                        pg.wait_for_timeout(1000)
                    if len(collected) > n0:
                        d = collected.pop(n0)
                        fn = d.suggested_filename or "download"
                        ext = os.path.splitext(fn)[1] or ".pdf"
                        out = os.path.join(DOC, item["save"] + ext)
                        d.save_as(out)
                        rec["saved"] = out
                        rec["suggested"] = fn
                        rec["status"] = "downloaded"
                        print("  >>> 已下载:", os.path.basename(out), "(" + fn + ")")
                        got = True
                        break
                    else:
                        print("  点击", prefer, "后 75s 无新下载事件；看是否登录墙…")
                        t = pg.inner_text("body")[:150].replace("\n", " ")
                        print("  当前页:", pg.title(), "|", t[:100])
            if not got:
                rec["status"] = "no_download"
        except Exception as e:
            rec["status"] = "error"
            rec["error"] = str(e)[:200]
            print("  ERR:", str(e)[:160])
        results.append(rec)

    json.dump(results, open(RESULT_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\n===== 汇总 =====")
    for r in results:
        print(" ", r["kw"][:32], "->", r["status"], r.get("saved", ""))
    print("结果 JSON:", RESULT_JSON)
    ctx.close()
