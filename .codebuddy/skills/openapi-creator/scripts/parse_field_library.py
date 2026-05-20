#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
通用 Word 文档表格解析器

从 .docx 解包后的 document.xml 中提取所有结构化表格，
输出为 JSON，不绑定任何业务领域。

用法:
    python parse_field_library.py [--input INPUT_XML] [--output OUTPUT_JSON] [--keywords KW1,KW2,...]

参数:
    --input    解包后的 document.xml 路径 (默认: ./field_library_unpacked/word/document.xml)
    --output   输出 JSON 路径 (默认: ./field_library_parsed.json)
    --keywords 逗号分隔的过滤关键词，匹配 heading 或单元格内容 (可选，不传则输出全量)
"""

import xml.etree.ElementTree as ET
import json
import argparse
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

NS = 'http://purl.oclc.org/ooxml/wordprocessingml/main'


# ────────────────────── 通用 XML 解析层 ──────────────────────

def get_cell_text(cell):
    """从 <w:tc> 中提取纯文本内容。"""
    texts = []
    for p in cell.findall(f'.//{{{NS}}}p'):
        line_texts = []
        for r in p.findall(f'.//{{{NS}}}r'):
            for t in r.findall(f'.//{{{NS}}}t'):
                if t.text:
                    line_texts.append(t.text)
        if line_texts:
            texts.append(''.join(line_texts))
    return ' '.join(texts).strip()


def _classify_table(header):
    """根据表头自动分类表格类型。

    约定:
      - field: 包含「标识符」或同时包含「名称」+ 「表示格式」的列 → 字段定义表
      - enum:  包含「代码」列 → 枚举值表
      - None:  不识别 → 跳过
    """
    has_identifier = any('标识符' in h for h in header)
    has_name_and_format = any('名称' in h for h in header) and any('表示格式' in h for h in header)
    has_code = any('代码' in h for h in header)

    if has_identifier or has_name_and_format:
        return 'field'
    if has_code:
        return 'enum'
    return None


def parse_tables(xml_path):
    """解析 document.xml，返回所有识别到的表格列表。

    每项结构:
    {
        "index":   int,     # 表格在文档中的序号（从 0 开始）
        "heading": str,     # 表格前方最近的标题文本
        "header":  [str],   # 表头列名
        "type":    str,     # "field" | "enum"
        "data":    [dict]   # 行数据，key 为表头列名
    }
    """
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError as e:
        print(f"Error: Failed to parse XML file '{xml_path}': {e}", file=sys.stderr)
        return []
    except OSError as e:
        print(f"Error: Failed to read XML file '{xml_path}': {e}", file=sys.stderr)
        return []

    root = tree.getroot()
    body = root.find(f'{{{NS}}}body')
    if body is None:
        print(f"Warning: No <w:body> found in '{xml_path}'", file=sys.stderr)
        return []

    current_heading = ""
    table_idx = 0
    results = []

    for child in list(body):
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if tag == 'p':
            pPr = child.find(f'{{{NS}}}pPr')
            if pPr is not None:
                pStyle = pPr.find(f'{{{NS}}}pStyle')
                if pStyle is not None:
                    val = pStyle.get(f'{{{NS}}}val', '')
                    if val and 'Heading' in val:
                        text = get_cell_text(child)
                        if text:
                            current_heading = text

        elif tag == 'tbl':
            rows = child.findall(f'{{{NS}}}tr')
            if len(rows) < 2:
                table_idx += 1
                continue

            header = [get_cell_text(c) for c in rows[0].findall(f'{{{NS}}}tc')]
            table_type = _classify_table(header)

            if table_type is not None:
                table_data = []
                for row in rows[1:]:
                    cells = [get_cell_text(c) for c in row.findall(f'{{{NS}}}tc')]
                    if cells and any(c.strip() for c in cells):
                        row_dict = {}
                        for i, h in enumerate(header):
                            if i < len(cells):
                                row_dict[h] = cells[i]
                        table_data.append(row_dict)

                results.append({
                    'index': table_idx,
                    'heading': current_heading,
                    'header': header,
                    'type': table_type,
                    'data': table_data
                })

            table_idx += 1

    return results


# ────────────────────── 搜索 / 过滤层 ──────────────────────

def filter_tables(results, keywords):
    """按关键词过滤表格，匹配 heading 或任意单元格内容（大小写不敏感）。

    Args:
        results:  parse_tables() 的返回值
        keywords: 关键词列表，如 ['车辆', '非机动车']

    Returns:
        匹配的子列表
    """
    if not keywords:
        return results

    kw_lower = [kw.lower() for kw in keywords]
    matched = []

    for r in results:
        heading_match = any(kw in r['heading'].lower() for kw in kw_lower)
        data_match = False
        for row in r['data']:
            for v in row.values():
                if any(kw in str(v).lower() for kw in kw_lower):
                    data_match = True
                    break
            if data_match:
                break

        if heading_match or data_match:
            matched.append(r)

    return matched


# ────────────────────── 格式化输出层 ──────────────────────

def print_tables(results, max_rows=30):
    """以可读格式打印表格摘要。"""
    for r in results:
        print(f"\n--- Table {r['index']}: [{r['type']}] {r['heading']} ---")
        print(f"Header: {r['header']}")
        for row in r['data'][:max_rows]:
            print(f"  {row}")
        if len(r['data']) > max_rows:
            print(f"  ... ({len(r['data']) - max_rows} more rows)")


def print_index(results):
    """打印所有表格的索引摘要。"""
    for r in results:
        print(f"  Table {r['index']}: [{r['type']}] {r['heading']} ({len(r['data'])} rows)")


# ────────────────────── CLI 入口 ──────────────────────

def main():
    parser = argparse.ArgumentParser(description='通用 Word 文档表格解析器')
    parser.add_argument('--input', default='./field_library_unpacked/word/document.xml',
                        help='解包后的 document.xml 路径')
    parser.add_argument('--output', default='./field_library_parsed.json',
                        help='输出 JSON 路径')
    parser.add_argument('--keywords', default='',
                        help='逗号分隔的过滤关键词（不传则输出全量）')
    args = parser.parse_args()

    # 1. 解析
    results = parse_tables(args.input)
    if not results:
        print(f"Error: No tables parsed from '{args.input}'. Check file path and format.", file=sys.stderr)
        sys.exit(1)

    # 2. 写全量 JSON
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Parsed {len(results)} tables -> {args.output}")
    except OSError as e:
        print(f"Error: Failed to write output to '{args.output}': {e}", file=sys.stderr)
        sys.exit(1)

    # 3. 打印索引
    print("\n=== TABLE INDEX ===\n")
    print_index(results)

    # 4. 按关键词过滤展示
    keywords = [kw.strip() for kw in args.keywords.split(',') if kw.strip()] if args.keywords else []
    if keywords:
        matched = filter_tables(results, keywords)
        print(f"\n=== MATCHED TABLES (keywords: {keywords}) ===")
        print(f"Matched: {len(matched)} / {len(results)}\n")
        print_tables(matched)
    else:
        print("\n=== ALL TABLES (no keyword filter) ===\n")
        print_tables(results)


if __name__ == '__main__':
    main()
