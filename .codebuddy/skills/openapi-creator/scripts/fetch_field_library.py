#!/usr/bin/env python3
"""
fetch_field_library.py - Fetch and parse the company standard field library document.

Downloads the standard field library (.doc/.docx) from the internal GitLab,
parses it into structured Markdown and JSON for AI reference and validation.

Usage:
    python fetch_field_library.py [--url URL] [--output-dir DIR] [--username USER] [--password PASS]

Dependencies:
    - python-docx (pip install python-docx)
    - LibreOffice (for .doc conversion, optional)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

try:
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx", file=sys.stderr)
    sys.exit(1)


# Default URL for the company standard field library
DEFAULT_URL = (
    "http://igcode.uniview.com/RD-UNIVIEW/public/module_guidelines/-/blob/main/"
    "%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%BA%A7%E5%93%81%E6%95%B0%E6%8D%AE%E9%A1%B9%E6%A0%87%E5%87%86.docx"
)

# For raw download, replace /blob/ with /raw/
RAW_URL_TEMPLATE = DEFAULT_URL.replace("/blob/", "/raw/")


def convert_doc_to_docx(doc_path: str) -> str:
    """
    Convert .doc to .docx using LibreOffice command line.
    Returns the path to the converted .docx file.
    """
    output_dir = os.path.dirname(doc_path)
    try:
        result = subprocess.run(
            [
                "soffice",
                "--headless",
                "--convert-to", "docx",
                "--outdir", output_dir,
                doc_path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            # Try alternative command names
            for cmd in ["libreoffice", "libreoffice7"]:
                try:
                    result = subprocess.run(
                        [cmd, "--headless", "--convert-to", "docx", "--outdir", output_dir, doc_path],
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )
                    if result.returncode == 0:
                        break
                except FileNotFoundError:
                    continue
            else:
                raise RuntimeError(f"LibreOffice conversion failed: {result.stderr}")

        base_name = os.path.splitext(os.path.basename(doc_path))[0]
        docx_path = os.path.join(output_dir, f"{base_name}.docx")
        if not os.path.exists(docx_path):
            raise FileNotFoundError(f"Converted file not found: {docx_path}")
        return docx_path
    except FileNotFoundError:
        raise RuntimeError(
            "LibreOffice not found. Please install LibreOffice for .doc conversion, "
            "or provide a .docx version of the document."
        )


def download_file(url: str, output_path: str) -> str:
    """
    Download a file from URL.
    Uses urllib to avoid external dependencies.
    Returns the path to the downloaded file.
    """
    import urllib.request
    import urllib.error

    # Handle authentication if needed
    request = urllib.request.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0")

    print(f"Downloading from: {url}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            with open(output_path, "wb") as f:
                f.write(response.read())
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("Authentication required. The document may need credentials.", file=sys.stderr)
            print("Try accessing the URL manually and providing the downloaded file.", file=sys.stderr)
        raise
    except urllib.error.URLError as e:
        print(f"Error: Network error while downloading '{url}': {e}", file=sys.stderr)
        raise
    except OSError as e:
        print(f"Error: IO error while saving to '{output_path}': {e}", file=sys.stderr)
        raise

    print(f"Downloaded to: {output_path}")
    return output_path


def download_via_browser(url: str, output_path: str, username: str = None, password: str = None) -> str:
    """
    Provide instructions for downloading via browser when direct download fails.
    This is a fallback method — the primary method should use chrome-devtools MCP.
    """
    print("=" * 60)
    print("Direct download failed. Please use one of these methods:")
    print("=" * 60)
    print()
    print("Method 1: Use chrome-devtools MCP (recommended)")
    print(f"  1. Navigate to: {url}")
    print("  2. Find the download button/link on the page")
    print(f"  3. Save the file to: {output_path}")
    print()
    print("Method 2: Manual download")
    print(f"  1. Open browser and visit: {url}")
    print(f"  2. Login with credentials if needed")
    print(f"  3. Download the file and save as: {output_path}")
    print()
    print(f"Then re-run this script with: --input {output_path}")
    print("=" * 60)

    return None


def parse_docx(docx_path: str) -> dict:
    """
    Parse a .docx file and extract field definitions from tables.
    Returns a structured dict with categories, fields, and enums.
    """
    try:
        doc = Document(docx_path)
    except Exception as e:
        print(f"Error: Failed to open .docx file '{docx_path}': {e}", file=sys.stderr)
        print("Hint: If you see KeyError about 'relationship type', try Method A (docx skill unpack + parse_field_library.py) instead.", file=sys.stderr)
        return {"source": os.path.basename(docx_path), "categories": [], "enums": []}

    result = {
        "source": os.path.basename(docx_path),
        "fetchTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "categories": [],
        "enums": [],
    }

    current_category = None
    current_fields = []

    def save_category():
        nonlocal current_category, current_fields
        if current_category and current_fields:
            result["categories"].append({
                "name": current_category,
                "fields": current_fields,
            })
        current_category = None
        current_fields = []

    # Extract paragraphs for category headings
    # and tables for field definitions
    for table_idx, element in enumerate(doc.element.body):
        tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

        if tag == "p":
            # Paragraph — might be a category heading
            para = Paragraph(element, doc)
            text = para.text.strip()
            if text and para.style and "Heading" in para.style.name:
                save_category()
                current_category = text
            elif text and not current_category:
                # First non-empty paragraph might be a category
                # Check if it looks like a heading (bold, larger font)
                runs = para.runs
                if runs and any(run.bold for run in runs if run.bold is not None):
                    save_category()
                    current_category = text

        elif tag == "tbl":
            # Table — extract field definitions or enum values
            table = Table(element, doc)
            rows = table.rows
            if len(rows) < 2:
                continue

            # Parse header row to identify column mapping
            header_cells = [cell.text.strip() for cell in rows[0].cells]
            col_map = _build_column_map(header_cells)

            if not col_map:
                continue

            header_str = "/".join(header_cells)
            # Check if this is an appendix enum table (代码/名称/说明)
            is_enum = "代码" in header_str and "名称" in header_str

            if is_enum:
                # Parse as enum table
                enums = []
                code_idx = col_map.get("enumCode", 0)
                name_idx = None
                desc_idx = col_map.get("description", None)
                for i, h in enumerate(header_cells):
                    if "名称" in h:
                        name_idx = i
                for row in rows[1:]:
                    cells = [cell.text.strip() for cell in row.cells]
                    enum_entry = {}
                    if code_idx < len(cells):
                        enum_entry["code"] = cells[code_idx]
                    if name_idx is not None and name_idx < len(cells):
                        enum_entry["name"] = cells[name_idx]
                    if desc_idx is not None and desc_idx < len(cells):
                        enum_entry["description"] = cells[desc_idx]
                    if enum_entry.get("code"):
                        enums.append(enum_entry)
                if enums:
                    result["enums"].append({
                        "table_index": table_idx,
                        "header": header_cells,
                        "category": current_category or f"附录表{len(result['enums'])+1}",
                        "values": enums,
                    })
            else:
                # Parse as field definition table
                # If no category yet, use a default
                if not current_category:
                    current_category = "默认分类"

                # Parse data rows
                for row in rows[1:]:
                    cells = [cell.text.strip() for cell in row.cells]
                    if len(cells) < 2:
                        continue

                    field = _extract_field(cells, col_map)
                    if field and field.get("fieldName"):
                        current_fields.append(field)

    # Save last category
    save_category()

    # If no categories found with paragraph+table approach,
    # try a simpler approach: treat each table as a category
    if not result["categories"] and not result["enums"]:
        result = _parse_tables_simple(doc)

    return result


def _build_column_map(headers: list) -> dict:
    """Build column index mapping from header row.
    
    Handles the specific document format:
    - Field definition tables: 序号/名称/标识符/表示格式/说明/引用的数据元
    - Appendix enum tables: 代码/名称/说明
    
    Key distinction: '名称' is the human-readable label, '标识符' is the programmatic field name.
    For fieldName, prefer '标识符' (identifier) over '名称' (label).
    """
    col_map = {}
    for i, h in enumerate(headers):
        h_lower = h.lower()
        # Field definition tables use '标识符' for the programmatic name
        if "标识符" in h or "identifier" in h_lower:
            col_map["fieldName"] = i
        elif any(kw in h_lower for kw in ["参数", "field", "param"]):
            col_map["fieldName"] = i
        # '名称' is the human-readable label, not the field identifier
        elif any(kw in h_lower for kw in ["名称"]) and "fieldName" not in col_map:
            col_map["fieldName"] = i
        if any(kw in h_lower for kw in ["类型", "type", "数据类型", "表示格式"]):
            col_map["dataType"] = i
        if any(kw in h_lower for kw in ["描述", "说明", "desc", "含义", "备注"]):
            col_map["description"] = i
        if any(kw in h_lower for kw in ["必须", "必填", "required", "是否"]):
            col_map["required"] = i
        if any(kw in h_lower for kw in ["分类", "类别", "category", "模块"]):
            col_map["category"] = i
        # Appendix enum tables use '代码' for code values
        if "代码" in h or "code" in h_lower:
            col_map["enumCode"] = i
    # If '名称' was mapped to fieldName but we also have '标识符', re-map '名称' to label
    if "标识符" in " ".join(headers):
        for i, h in enumerate(headers):
            if "名称" in h:
                col_map["fieldLabel"] = i
                if col_map.get("fieldName") == i:
                    # '标识符' already took precedence, no conflict
                    pass
                break
    return col_map


def _extract_field(cells: list, col_map: dict) -> dict:
    """Extract a field definition from a table row."""
    field = {}
    for key, idx in col_map.items():
        if idx < len(cells):
            field[key] = cells[idx]
    # Ensure fieldName is not empty or just a dash (placeholder row)
    name = field.get("fieldName", "").strip()
    if name in ("-", "", "—"):
        field.pop("fieldName", None)
    return field


def _parse_tables_simple(doc: Document) -> dict:
    """
    Simple fallback parser: treat each table as a separate category.
    Handles both field definition tables and appendix enum tables.
    """
    result = {
        "source": os.path.basename(doc.part.blob if hasattr(doc.part, 'blob') else "unknown"),
        "fetchTime": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "categories": [],
        "enums": [],
    }

    for idx, table in enumerate(doc.tables):
        rows = table.rows
        if len(rows) < 2:
            continue

        header_cells = [cell.text.strip() for cell in rows[0].cells]
        header_str = "/".join(header_cells)
        col_map = _build_column_map(header_cells)

        if not col_map:
            continue

        # Check if this is an appendix enum table (代码/名称/说明)
        is_enum = "代码" in header_str and "名称" in header_str

        if is_enum:
            # Parse as enum table
            enums = []
            code_idx = col_map.get("enumCode", 0)
            name_idx = None
            desc_idx = col_map.get("description", None)
            for i, h in enumerate(header_cells):
                if "名称" in h:
                    name_idx = i
            for row in rows[1:]:
                cells = [cell.text.strip() for cell in row.cells]
                enum_entry = {}
                if code_idx < len(cells):
                    enum_entry["code"] = cells[code_idx]
                if name_idx is not None and name_idx < len(cells):
                    enum_entry["name"] = cells[name_idx]
                if desc_idx is not None and desc_idx < len(cells):
                    enum_entry["description"] = cells[desc_idx]
                if enum_entry.get("code"):
                    enums.append(enum_entry)
            if enums:
                result["enums"].append({
                    "table_index": idx,
                    "header": header_cells,
                    "values": enums,
                })
        else:
            # Parse as field definition table
            fields = []
            for row in rows[1:]:
                cells = [cell.text.strip() for cell in row.cells]
                field = _extract_field(cells, col_map)
                if field and field.get("fieldName"):
                    fields.append(field)

            if fields:
                result["categories"].append({
                    "name": f"分类{idx + 1}",
                    "fields": fields,
                })

    return result


def to_markdown(data: dict) -> str:
    """Convert parsed field library data to Markdown format."""
    lines = []
    lines.append(f"# {data.get('source', '标准字段库')}")
    lines.append("")
    lines.append(f"> 获取时间: {data.get('fetchTime', 'N/A')}")
    lines.append("")

    for category in data.get("categories", []):
        lines.append(f"## {category['name']}")
        lines.append("")

        fields = category.get("fields", [])
        if not fields:
            lines.append("(无字段定义)")
            lines.append("")
            continue

        # Build table header
        all_keys = set()
        for f in fields:
            all_keys.update(f.keys())

        # Preferred column order
        col_order = ["fieldName", "fieldLabel", "dataType", "required", "description"]
        cols = [c for c in col_order if c in all_keys]
        cols.extend(sorted(all_keys - set(cols)))

        # Header row
        header_names = {
            "fieldName": "标识符",
            "fieldLabel": "名称",
            "dataType": "数据类型",
            "required": "是否必须",
            "description": "描述",
        }
        headers = [header_names.get(c, c) for c in cols]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(cols)) + " |")

        # Data rows
        for f in fields:
            row = []
            for c in cols:
                val = f.get(c, "")
                # Clean up whitespace
                val = re.sub(r"\s+", " ", val).strip()
                row.append(val)
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")

    # Append enum tables
    for enum_table in data.get("enums", []):
        category = enum_table.get("category", "附录")
        lines.append(f"## {category}")
        lines.append("")

        headers = [h for h in enum_table.get("header", []) if h]
        if not headers:
            headers = ["代码", "名称", "说明"]

        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for v in enum_table.get("values", []):
            row = []
            for h in headers:
                if "代码" in h or "code" in h.lower():
                    row.append(v.get("code", ""))
                elif "名称" in h or "name" in h.lower():
                    row.append(v.get("name", ""))
                elif "说明" in h or "desc" in h.lower():
                    row.append(v.get("description", ""))
                else:
                    row.append("")
            lines.append("| " + " | ".join(row) + " |")

        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Fetch and parse the company standard field library")
    parser.add_argument("--url", default=None, help="Document URL (default: internal GitLab)")
    parser.add_argument("--input", dest="input_file", default=None, help="Local .doc/.docx file path (skip download)")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current directory)")
    parser.add_argument("--username", default=None, help="Username for authentication")
    parser.add_argument("--password", default=None, help="Password for authentication")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    if args.input_file:
        # Use local file
        file_path = args.input_file
        print(f"Using local file: {file_path}")
    else:
        # Download from URL
        url = args.url or RAW_URL_TEMPLATE
        is_raw = "/raw/" in url
        ext = ".docx" if url.endswith(".docx") else ".doc"

        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, f"field_library{ext}")

        try:
            download_file(url, file_path)
        except Exception as e:
            print(f"Direct download failed: {e}", file=sys.stderr)
            result = download_via_browser(url, file_path, args.username, args.password)
            if result is None:
                # Check if user has placed the file manually
                if os.path.exists(file_path):
                    print(f"File found at: {file_path}")
                else:
                    print("No file available. Exiting.", file=sys.stderr)
                    sys.exit(1)

    # Convert .doc to .docx if needed
    if file_path.endswith(".doc") and not file_path.endswith(".docx"):
        print("Converting .doc to .docx...")
        try:
            file_path = convert_doc_to_docx(file_path)
            print(f"Converted to: {file_path}")
        except RuntimeError as e:
            print(f"Conversion failed: {e}", file=sys.stderr)
            sys.exit(1)

    # Parse the document
    print("Parsing document...")
    data = parse_docx(file_path)
    if not data.get("categories") and not data.get("enums"):
        print("Error: No field definitions or enum tables found in the document.", file=sys.stderr)
        sys.exit(1)

    # Count total fields and enums
    total_fields = sum(len(c.get("fields", [])) for c in data.get("categories", []))
    total_enums = sum(len(e.get("values", [])) for e in data.get("enums", []))
    print(f"Found {len(data['categories'])} categories ({total_fields} fields), {len(data.get('enums', []))} enum tables ({total_enums} values)")

    # Output Markdown
    md_path = os.path.join(args.output_dir, "field_library.md")
    try:
        md_content = to_markdown(data)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"Markdown output: {md_path}")
    except OSError as e:
        print(f"Error: Failed to write Markdown to '{md_path}': {e}", file=sys.stderr)

    # Output JSON
    json_path = os.path.join(args.output_dir, "field_library.json")
    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"JSON output: {json_path}")
    except (OSError, TypeError) as e:
        print(f"Error: Failed to write JSON to '{json_path}': {e}", file=sys.stderr)
        sys.exit(1)

    print("Done!")


if __name__ == "__main__":
    main()
