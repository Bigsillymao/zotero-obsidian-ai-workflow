# -*- coding: utf-8 -*-
"""生成自测样例文件（默认写入 tests/_fixtures/；该目录已在 .gitignore 中）。

  table_demo.xlsx   两个工作表（中文表头 + 浮点/文本）
  table_gbk.csv     GBK 编码 CSV
  fake_html.xls     伪装成 .xls 的 HTML 表格（GBK + <style> 前缀 + colspan）
  old_binary.xls    仅有 CFB 文件头的假 .xls（用于验证引导分支）
  demo.html         供 LibreOffice 转 PDF 的样例文档（标题 + 段落 + 表格）

用法：
  python tests/make_test_files.py [输出目录]

⚠ 生成的测试产物（尤其经 LibreOffice 等外部工具转换出的文件）可能携带该工具写入的
   文档属性；请勿把 _fixtures 目录提交或上传，需要时随时重新生成即可。
"""
import sys
from pathlib import Path


def make_xlsx(path: Path) -> None:
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = '击实试验'
    ws.append(['含水率/%', '干密度/(g/cm3)', '备注'])
    ws.append([12.5, 1.62, '第1组'])
    ws.append([14.0, 1.71, '第2组'])
    ws.append([15.5, 1.75, '第3组'])
    ws.append([17.0, 1.73, '曲线峰值附近'])
    ws2 = wb.create_sheet('颗粒分析')
    ws2.append(['粒径/mm', '小于某粒径质量百分比/%'])
    ws2.append([2.0, 100.0])
    ws2.append([0.075, 62.3])
    ws2.append([0.005, 21.8])
    wb.save(path)


def make_gbk_csv(path: Path) -> None:
    text = '试件编号,抗压强度/MPa,跨距/mm\nA-1,3.25,100\nA-2,3.41,100\nB-1,2.98,70\n'
    path.write_bytes(text.encode('gbk'))


def make_fake_xls(path: Path) -> None:
    # 典型的高校教务/综测系统导出：HTML 伪装 .xls，GBK 编码，开头 <style> 干扰解析
    html = ('<html><head><meta http-equiv="Content-Type" '
            'content="text/html; charset=gb2312">\n'
            '<style>td{mso-number-format:"\\@";} .x{font-family:宋体;}</style>'
            '</head><body>\n'
            '<table border=1>\n'
            ' <tr><td colspan=3 align=center>2026年春季学期成绩汇总（系统导出）</td></tr>\n'
            ' <tr><td>学号</td><td>姓名</td><td>总分</td></tr>\n'
            ' <tr><td>2026001</td><td>张三</td><td>92.5</td></tr>\n'
            ' <tr><td>2026002</td><td>李四</td><td>88</td></tr>\n'
            '</table>\n</body></html>')
    path.write_bytes(html.encode('gbk'))


def make_old_binary_xls(path: Path) -> None:
    # CFB (Compound File Binary) 文件头，后面是占位字节
    path.write_bytes(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1' + b'\x00' * 504)


def make_html(path: Path) -> None:
    html = ('<!doctype html><html><head><meta charset="utf-8">'
            '<title>文档转换自测样例</title></head><body>\n'
            '<h1>文档转换自测样例</h1>\n'
            '<p>本段用于验证 MinerU 的段落还原与页标记输出。</p>\n'
            '<table><tr><th>试验</th><th>数值</th></tr>'
            '<tr><td>液限</td><td>32.4</td></tr>'
            '<tr><td>塑限</td><td>18.1</td></tr></table>\n'
            '</body></html>')
    path.write_text(html, encoding='utf-8')


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / '_fixtures'
    out.mkdir(parents=True, exist_ok=True)
    make_xlsx(out / 'table_demo.xlsx')
    make_gbk_csv(out / 'table_gbk.csv')
    make_fake_xls(out / 'fake_html.xls')
    make_old_binary_xls(out / 'old_binary.xls')
    make_html(out / 'demo.html')
    print('fixtures written to:', out)


if __name__ == '__main__':
    main()
