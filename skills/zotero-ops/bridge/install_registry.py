# -*- coding: utf-8 -*-
"""把 ZCode Bridge 插件注册进 Zotero 的 extensions.json（需在 Zotero 关闭时运行）。

⚠ 仅用于「常规侧载被禁用」的 Zotero 版本（实测于 Zotero 9.x）。
   Zotero 7 / 8 通常可直接用「工具 → 插件 → Install Plugin From File…」安装 XPI，无需本脚本。

原理：以已装插件的注册条目为模板克隆，再替换字段；并删除 addonStartup.json.lz4 强制重建。

用法：
    python install_registry.py [Zotero profile 目录]
  或先设置环境变量 ZOTERO_PROFILE。
  不传时自动在 %APPDATA%\\Zotero\\Zotero\\Profiles 下查找 *.default*。
  （macOS profile 一般在 ~/Library/Application Support/Zotero/...；Linux 在 ~/.zotero/...，
    请显式传入或设置 ZOTERO_PROFILE。）
"""
import glob, json, os, shutil, sys, time, uuid


def find_profile() -> str:
    p = (sys.argv[1] if len(sys.argv) > 1 else '') or os.environ.get('ZOTERO_PROFILE', '')
    if p:
        return os.path.expanduser(p)
    appdata = os.environ.get('APPDATA', '')
    if appdata:
        cands = glob.glob(os.path.join(appdata, 'Zotero', 'Zotero', 'Profiles', '*.default*'))
        if len(cands) == 1:
            return cands[0]
        if cands:
            print('发现多个 profile，使用第一个：', cands[0])
            return cands[0]
    sys.exit('未找到 Zotero profile：请把 profile 目录作为参数传入，或设置环境变量 ZOTERO_PROFILE。')


PROFILE = find_profile()
EXT = os.path.join(PROFILE, 'extensions')
XPI = os.path.join(EXT, 'zcode-bridge@zcode.local.xpi')
EJSON = os.path.join(PROFILE, 'extensions.json')
LZ4 = os.path.join(PROFILE, 'addonStartup.json.lz4')

if not os.path.exists(XPI):
    sys.exit('XPI 不存在: ' + XPI + '\n（先把 zcode-bridge.xpi 复制到该位置）')

for f in (EJSON, LZ4):
    if os.path.exists(f) and not os.path.exists(f + '.bak-zcode'):
        shutil.copy2(f, f + '.bak-zcode')
        print('已备份:', os.path.basename(f) + '.bak-zcode')

d = json.loads(open(EJSON, encoding='utf-8-sig').read())
addons = d['addons']

# 模板：优先用 ZotMoov 的条目；没有则退回任意一个现有插件条目
tmpl = next((a for a in addons if isinstance(a, dict) and a.get('id') == 'zotmoov@wileyy.com'), None)
if tmpl is None:
    tmpl = next((a for a in addons if isinstance(a, dict) and a.get('id')), None)
if tmpl is None:
    sys.exit('extensions.json 中没有可用作模板的现有插件条目（可先安装任意一个插件再运行本脚本）。')

new = json.loads(json.dumps(tmpl))  # 深拷贝模板
now = int(time.time() * 1000)
new.update({
    'id': 'zcode-bridge@zcode.local',
    'syncGUID': '{' + str(uuid.uuid4()) + '}',
    'version': '0.1.0',
    'updateURL': None,
    'defaultLocale': {
        'name': 'ZCode Bridge',
        'description': 'Local HTTP bridge (/zcode/*) for AI agents: full item/collection/tag/attachment operations.',
        'creator': 'ZCode', 'developers': None, 'translators': None, 'contributors': None,
    },
    'installDate': now,
    'updateDate': now,
    'path': XPI,
    'sourceURI': None,
    'targetApplications': [{'id': 'zotero@zotero.org', 'minVersion': '6.999', 'maxVersion': '10.*'}],
    'installTelemetryInfo': None,
    'rootURI': 'jar:file:///' + XPI.replace('\\', '/') + '!/',
    'location': 'app-profile',
    'active': True, 'userDisabled': False, 'appDisabled': False,
    'softDisabled': False, 'seen': True, 'foreignInstall': False,
})

addons = [a for a in addons if a.get('id') != new['id']] + [new]
d['addons'] = addons
open(EJSON, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False))
print('extensions.json 已写入，插件共', len(addons), '个:', [a.get('id') for a in addons])

if os.path.exists(LZ4):
    os.remove(LZ4)
    print('addonStartup.json.lz4 已删除（强制从 JSON 重建）')
else:
    print('addonStartup.json.lz4 不存在（无需删除）')
