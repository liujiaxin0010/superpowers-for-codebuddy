#!/usr/bin/env python3
"""
convert_field_lib.py - Convert field_library_parsed.json (array format) 
to the standard format expected by validate_api.py.

The docx parser outputs: [{...}, {...}, ...]
The validator expects:   {"categories": [{"name": "all_fields", "fields": [...]}]}

Also supports extracting field names from field_library_full.txt (the raw text export).

Usage:
    python convert_field_lib.py --input field_library_full.txt --output field_lib_standard.json
    python convert_field_lib.py --input field_library_parsed.json --output field_lib_standard.json
"""

import argparse
import json
import os
import re
import sys


def _extract_from_table_rows(data: list) -> dict:
    """Convert from parse_field_library.py output: [{index, heading, header, type, data: [{col: val}]}].

    Two table types are handled:
      - "field": rows contain '标识符' key → extract fieldName/fieldLabel/dataType/description
      - "enum":  rows contain '代码' key → extract enum code/name/description
    """
    fields = []
    enums = []

    for table in data:
        table_type = table.get("type", "")
        heading = table.get("heading", "")
        rows = table.get("data", [])

        if table_type == "field":
            for row in rows:
                name = row.get("标识符", "").strip()
                label = row.get("名称", "").strip()
                fmt = row.get("表示格式", "").strip()
                desc = row.get("说明", "").strip()
                ref = row.get("引用的数据元", "").strip()
                if name and name not in ("-", "—"):
                    field = {"fieldName": name, "fieldLabel": label}
                    if fmt:
                        field["dataType"] = fmt
                    if desc:
                        field["description"] = desc
                    if ref:
                        field["reference"] = ref
                    fields.append(field)

        elif table_type == "enum":
            values = []
            for row in rows:
                code = row.get("代码", "").strip()
                ename = row.get("名称", "").strip()
                edesc = row.get("说明", "").strip()
                if code:
                    entry = {"code": code, "name": ename}
                    if edesc:
                        entry["description"] = edesc
                    values.append(entry)
            if values:
                enums.append({
                    "category": heading,
                    "values": values,
                })

    result = {"categories": [{"name": "all_fields", "fields": fields}]}
    if enums:
        result["enums"] = enums
    return result


def convert_from_parsed_json(input_path: str) -> dict:
    """Convert from field_library_parsed.json (various formats) or fetch_field_library.py output."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error: Failed to parse JSON file '{input_path}': {e}", file=sys.stderr)
        return {"categories": []}
    except OSError as e:
        print(f"Error: Failed to read file '{input_path}': {e}", file=sys.stderr)
        return {"categories": []}

    if isinstance(data, dict):
        # Already in standard format from fetch_field_library.py
        if "categories" in data:
            return data

        # Old format from custom parser: {"field_definitions": [...], "enum_tables": [...]}
        if "field_definitions" in data:
            fields = []
            for td in data["field_definitions"]:
                for item in td.get("fields", []):
                    name = item.get("identifier") or item.get("fieldName") or item.get("标识符") or ""
                    label = item.get("name") or item.get("fieldLabel") or item.get("名称") or ""
                    if name:
                        fields.append({"fieldName": name.strip(), "fieldLabel": label.strip()})
            result = {"categories": [{"name": "all_fields", "fields": fields}]}
            if "enum_tables" in data:
                result["enums"] = data["enum_tables"]
            return result

    if isinstance(data, list):
        # New format from parse_field_library.py: [{index, heading, header, type, data}]
        first = data[0] if data else {}
        if "index" in first and "type" in first and "data" in first:
            return _extract_from_table_rows(data)

        # Legacy array format: flat list of field items
        fields = []
        for item in data:
            name = item.get("identifier") or item.get("fieldName") or item.get("标识符") or ""
            label = item.get("name") or item.get("fieldLabel") or item.get("名称") or ""
            if name:
                fields.append({"fieldName": name.strip(), "fieldLabel": label.strip()})
        return {"categories": [{"name": "all_fields", "fields": fields}]}

    return {"categories": []}


def convert_from_full_txt(input_path: str) -> dict:
    """Convert from field_library_full.txt (raw text export from docx)."""
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            txt = f.read()
    except (UnicodeDecodeError, OSError) as e:
        print(f"Error: Failed to read text file '{input_path}': {e}", file=sys.stderr)
        return {"categories": []}

    fields = []
    lines = txt.split("\n")
    for line in lines:
        # Pattern: ["", "名称", "标识符", ...]
        m = re.match(r'\["",\s+"(.+?)",\s+"(\w+)"', line)
        if m:
            fields.append({"fieldName": m.group(2).strip(), "fieldLabel": m.group(1).strip()})

    return {"categories": [{"name": "all_fields", "fields": fields}]}


def main():
    parser = argparse.ArgumentParser(description="Convert field library to standard format for validate_api.py")
    parser.add_argument("--input", required=True, help="Input file (field_library_parsed.json or field_library_full.txt)")
    parser.add_argument("--output", required=True, help="Output file (field_lib_standard.json)")
    args = parser.parse_args()

    input_path = args.input

    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    if input_path.endswith(".json"):
        result = convert_from_parsed_json(input_path)
    elif input_path.endswith(".txt"):
        result = convert_from_full_txt(input_path)
    else:
        print(f"Error: Unsupported input format: {input_path}", file=sys.stderr)
        sys.exit(1)

    field_count = len(result["categories"][0]["fields"]) if result.get("categories") else 0

    try:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"Error: Failed to write output to '{args.output}': {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Converted {field_count} fields from {input_path} -> {args.output}")


if __name__ == "__main__":
    main()
