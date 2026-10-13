# -*- coding: utf-8 -*-
"""CNKI 拼图滑块自动求解（模板）：截取背景图与滑块图 → 零均值归一化互相关找缺口 → 仿人拖动。
成功后 Cookie 存进持久化 profile，后续检索免验证。

环境变量：
  CNKI_PROFILE  持久浏览器 profile 目录（默认 ~/.cnki-browser-profile）
  CNKI_KW       用于触发/验证的检索词（默认示例占位词）
"""
import os, tempfile, time, urllib.parse
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

UD = os.environ.get("CNKI_PROFILE") or os.path.expanduser("~/.cnki-browser-profile")
T = tempfile.gettempdir()
KW = os.environ.get("CNKI_KW", "<一个用于触发验证页的检索词>")
URL = "https://kns.cnki.net/kns8s/defaultresult/index?kw=" + urllib.parse.quote(KW) + "&korder=TI"


def find_gap_x(bg_path, piece_path, y_offset=0):
    bg = np.array(Image.open(bg_path).convert("L")).astype(np.float32)
    pc = np.array(Image.open(piece_path).convert("L")).astype(np.float32)
    h, w = pc.shape
    if bg.shape[0] < y_offset + h:
        y_offset = max(0, bg.shape[0] - h)
    band = bg[y_offset:y_offset + h, :]
    H, W = band.shape
    pc0 = pc - pc.mean()
    denom_p = float(np.sqrt((pc0 ** 2).sum())) or 1.0
    best_score, best_x = -2.0, 0
    for x in range(0, max(1, W - w + 1)):
        win = band[:, x:x + w]
        win0 = win - win.mean()
        denom_w = float(np.sqrt((win0 ** 2).sum())) or 1.0
        score = float((win0 * pc0).sum()) / (denom_w * denom_p)
        if score > best_score:
            best_score, best_x = score, x
    return best_x, best_score


with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        UD, headless=False, channel="msedge", locale="zh-CN",
        viewport={"width": 1400, "height": 900}, accept_downloads=True,
        args=["--disable-blink-features=AutomationControlled"],
    )
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()

    for attempt in range(1, 4):
        pg.goto(URL, timeout=90000, wait_until="domcontentloaded")
        pg.wait_for_timeout(6000)
        title = pg.title()
        print(f"[尝试 {attempt}] TITLE: {title}")
        if "安全验证" not in title:
            print(">>> 已通过（或无验证），结束")
            break

        # 截图元素
        bgBox = pg.locator(".verify-img-panel").first.bounding_box()
        pcBox = pg.locator(".verify-sub-block").first.bounding_box()
        hdBox = pg.locator(".verify-move-block").first.bounding_box()
        if not (bgBox and pcBox and hdBox):
            print("  元素找不到，退出")
            break
        pg.locator(".verify-img-panel").first.screenshot(path=os.path.join(T, "cnki_bg.png"))
        pg.locator(".verify-sub-block").first.screenshot(path=os.path.join(T, "cnki_piece.png"))

        y_off = int(round(pcBox["y"] - bgBox["y"]))
        gap_x, score = find_gap_x(os.path.join(T, "cnki_bg.png"), os.path.join(T, "cnki_piece.png"), y_off)
        print(f"  缺口检测: x={gap_x} (相关度 {score:.3f}) | 背景宽 {bgBox['width']:.0f} 滑块宽 {pcBox['width']:.0f}")

        # 需要的位移：滑块中心 → 缺口中心
        dx = (bgBox["x"] + gap_x) + pcBox["width"] / 2 - (pcBox["x"] + pcBox["width"] / 2)
        print(f"  拖动距离: {dx:.1f}px")
        if dx < 5:
            dx = 5

        sx = hdBox["x"] + hdBox["width"] / 2
        sy = hdBox["y"] + hdBox["height"] / 2
        pg.mouse.move(sx, sy)
        pg.mouse.down()
        steps = 34
        for i in range(1, steps + 1):
            t = i / steps
            ease = 3 * t * t - 2 * t * t * t
            jy = (1 if i % 4 < 2 else -1) * 0.6
            pg.mouse.move(sx + dx * ease, sy + jy)
            time.sleep(0.011)
        time.sleep(0.35)
        pg.mouse.move(sx + dx, sy)  # 落点微调
        time.sleep(0.15)
        pg.mouse.up()
        pg.wait_for_timeout(5000)
        t2 = pg.title()
        print(f"  拖动后 TITLE: {t2}")
        if "安全验证" not in t2:
            print(">>> 验证通过！")
            break
        body = pg.inner_text("body")[:120].replace("\n", " ")
        print("  提示:", body)

    # 通过后：抓取结果页结构（供下一步下载脚本使用）
    if "安全验证" not in pg.title():
        pg.wait_for_timeout(4000)
        rows = pg.evaluate("""() => {
          const out = [];
          document.querySelectorAll('a').forEach(a => {
            const t = (a.innerText || '').trim();
            if (t.length > 8 && /kcms|abstract|detail/i.test(a.href || '')) out.push({t: t.slice(0,60), h: a.href});
          });
          return out.slice(0, 10);
        }""")
        print("结果链接样例:")
        for r in rows:
            print("  -", r["t"], "->", r["h"][:100])
        if not rows:
            txt = pg.inner_text("body")[:300].replace("\n", " ")
            print("页面片段:", txt)

    ctx.close()
    print("DONE")
