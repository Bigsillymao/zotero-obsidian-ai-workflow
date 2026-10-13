# -*- coding: utf-8 -*-
"""表格 -> Markdown（仅供快速阅读；数值核校请读原始文件）。

支持：
  .xlsx / .csv      直接转换
  .xls              自动探测：伪装成 .xls 的 HTML 表格（各类系统导出常见）按 HTML 解析；
                    真·二进制 .xls 提示先用 LibreOffice 转 .xlsx
  .html / .htm      HTML 中的 <table> 转 Markdown 表格（colspan/rowspan 展开）

用法：
  python xlsx-to-md.py "表格.xlsx" [-o 输出.md]
  python xlsx-to-md.py "成绩单.xls"
  python xlsx-to-md.py data.csv

依赖：openpyxl（xlsx）；beautifulsoup4（HTML 表格解析）
"""
import argparse
import csv
from pathlib import Path

HTML_EXTS = ('.xls', '.html', '.htm')


def md_escape(s: str) -> str:
    return str(s).replace('|', '\\|').replace('\n', '<br>')


def cell(v) -> str:
    if v is None:
        return ''
    if isinstance(v, float):
        # 保留原始精度显示（不改变数值），科学计数法避免长尾
        return repr(v) if abs(v) >= 1e-4 or v == 0 else f'{v:.6g}'
    return md_escape(v)


def table_to_md(rows) -> str:
    rows = [list(r) for r in rows]
    if not rows:
        return '_(空表)_\n'
    ncol = max(len(r) for r in rows)
    rows = [r + [''] * (ncol - len(r)) for r in rows]
    header, body = rows[0], rows[1:]
    out = ['| ' + ' | '.join(cell(c) for c in header) + ' |',
           '| ' + ' | '.join(['---'] * ncol) + ' |']
    for r in body:
        out.append('| ' + ' | '.join(cell(c) for c in r) + ' |')
    return '\n'.join(out) + '\n'


def convert_xlsx(path: Path) -> str:
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True, read_only=True)
    parts = [f'# {path.stem}\n']
    for ws in wb.worksheets:
        parts.append(f'## 工作表：{ws.title}\n')
        parts.append(table_to_md(ws.iter_rows(values_only=True)))
        parts.append('')
    wb.close()
    return '\n'.join(parts)


def convert_csv(path: Path) -> str:
    # 尝试 utf-8(-sig) 与 gb18030（GBK 超集）
    for enc in ('utf-8-sig', 'gb18030'):
        try:
            with open(path, 'r', encoding=enc, newline='') as f:
                rows = list(csv.reader(f))
            return f'# {path.stem}\n\n' + table_to_md(rows)
        except UnicodeDecodeError:
            continue
    raise SystemExit('无法解码 CSV（尝试过 utf-8 / gb18030）')


def _decode(raw: bytes) -> str:
    for enc in ('utf-8-sig', 'gb18030', 'utf-16'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return raw.decode('gb18030', errors='replace')


def looks_like_html(path: Path) -> bool:
    head = _decode(path.read_bytes()[:4096]).lower()
    return ('<html' in head) or ('<table' in head) or ('<tr' in head)


def html_table_to_rows(table) -> list:
    """把 bs4 的 <table> 展平成二维表；colspan/rowspan 展开，文本放合并区左上角。"""
    grid = {}
    max_col = 0
    for r, tr in enumerate(table.find_all('tr')):
        c = 0
        for td in tr.find_all(['td', 'th']):
            while (r, c) in grid:
                c += 1
            text = td.get_text(' ', strip=True)
            try:
                cs = max(1, int(td.get('colspan') or 1))
            except ValueError:
                cs = 1
            try:
                rs = max(1, int(td.get('rowspan') or 1))
            except ValueError:
                rs = 1
            for dr in range(rs):
                for dc in range(cs):
                    grid[(r + dr, c + dc)] = text if (dr == 0 and dc == 0) else ''
            c += cs
            if c > max_col:
                max_col = c
    nrow = max((r for r, _ in grid), default=-1) + 1
    rows = [[grid.get((r, c), '') for c in range(max_col)] for r in range(nrow)]
    rows = [r for r in rows if any(str(x).strip() for x in r)]  # 去全空行
    while rows and all(not str(r[-1]).strip() for r in rows):    # 去全空尾列
        rows = [r[:-1] for r in rows]
    return rows


def convert_html(path: Path) -> str:
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise SystemExit('解析 HTML 表格需要 beautifulsoup4：pip install beautifulsoup4')
    soup = BeautifulSoup(_decode(path.read_bytes()), 'html.parser')
    tables = soup.find_all('table')
    if not tables:
        raise SystemExit(f'未在该文件中找到 <table>：{path}')
    parts = [f'# {path.stem}\n']
    n = 0
    for t in tables:
        rows = html_table_to_rows(t)
        if not rows:
            continue
        n += 1
        parts.append(f'## 表格 {n}\n')
        parts.append(table_to_md(rows))
        parts.append('')
    if n == 0:
        raise SystemExit(f'找到 <table> 但内容为空：{path}')
    return '\n'.join(parts)


def main():
    ap = argparse.ArgumentParser(
        description='表格 -> Markdown（仅供阅读；数值核校请读原始文件）')
    ap.add_argument('input')
    ap.add_argument('-o', '--out', default=None)
    args = ap.parse_args()
    src = Path(args.input)
    if not src.exists():
        raise SystemExit(f'文件不存在: {src}')
    suf = src.suffix.lower()

    if suf == '.xlsx':
        md = convert_xlsx(src)
    elif suf in HTML_EXTS:
        if suf == '.xls' and not looks_like_html(src):
            raise SystemExit(
                '这是真·二进制 .xls（Excel 97-2003），本脚本不直接解析。\n'
                '先转换，例如：\n'
                f'  soffice --headless --convert-to xlsx "{src}"\n'
                '（或用 Excel 另存为 .xlsx）再用本脚本转 .xlsx。')
        if suf == '.xls':
            print('[note] 该 .xls 实为 HTML 表格（系统导出常见），按 HTML 解析。')
        md = convert_html(src)
    elif suf in ('.csv', '.txt'):
        md = convert_csv(src)
    else:
        raise SystemExit('支持: .xlsx / .csv / .html / .xls(HTML 伪装)；'
                         '真 .xls 请先转 .xlsx')
    out = Path(args.out) if args.out else src.with_suffix('.md')
    out.write_text(md, encoding='utf-8')
    print(f'MD: {out}')


if __name__ == '__main__':
    main()
