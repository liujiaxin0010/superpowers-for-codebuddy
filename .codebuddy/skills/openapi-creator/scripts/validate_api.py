#!/usr/bin/env python3
"""
validate_api.py - Validate OpenAPI interface definitions against the specification.

Validates a Markdown interface definition document against:
  A. Specification compliance rules (from 平台类OpenAPI接口定义规范)
  B. Business logic rules
  C. Field consistency (against company standard field library JSON)

Usage:
    python validate_api.py --api-doc PATH [--field-lib PATH] [--output PATH]

Dependencies:
    - PyYAML (pip install pyyaml) — optional, for YAML output
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Severity(Enum):
    CRITICAL = "critical"    # Must fix (violates a rule)
    WARNING = "warning"      # Suggested fix (violates a recommendation)
    INFO = "info"             # Informational


@dataclass
class ValidationIssue:
    id: str
    severity: Severity
    location: str
    message: str
    suggestion: str = ""


@dataclass
class FieldDef:
    name: str
    data_type: str
    required: str
    description: str
    reference: str = ""  # 字段标准引用


@dataclass
class ApiEndpoint:
    name: str
    url: str
    method: str = "POST"
    description: str = ""
    notes: str = ""
    request_fields: List[FieldDef] = field(default_factory=list)
    response_fields: List[FieldDef] = field(default_factory=list)
    response_data_fields: List[FieldDef] = field(default_factory=list)
    raw_section: str = ""


# ============================================================
# Allowed values per the specification
# ============================================================

ALLOWED_BASIC_TYPES = {"integer", "number", "string"}
ALLOWED_COMPLEX_TYPES = {"array", "object"}
ALLOWED_ALL_TYPES = ALLOWED_BASIC_TYPES | ALLOWED_COMPLEX_TYPES

SERVICE_URI_LIST = [
    "resource", "gateway", "device", "event", "system",
    "video", "acs", "visitor", "vis", "parking",
    "vts", "pts", "cfs", "ecs", "sws",
    "tas", "as", "devOps", "smart",
]

ACTION_LIST = [
    "add", "delete", "update", "search", "get",
    "set", "on", "off", "start", "stop",
    "invoke", "upgrade", "import", "export",
]

# Regex for lowerCamelCase: starts with lowercase, then alphanumeric
LOWER_CAMEL_RE = re.compile(r'^[a-z][a-zA-Z0-9]*$')

# Regex to detect array element sub-field paths (e.g., "list[].fieldName", "successList[].code")
ARRAY_ELEMENT_PATH_RE = re.compile(r'\[\]')

# URL pattern: /openAPI/{serviceURI}/v{N}/{resource}[/{child}]/{action}
# ServiceURI can be any lowerCamelCase word (not limited to known list — V-12 handles that separately)
URL_PATTERN = re.compile(
    r'^/openAPI/[a-zA-Z][a-zA-Z0-9]*/v\d+/[a-zA-Z0-9]+'
    r'(?:/[a-zA-Z0-9]+)?/[a-zA-Z0-9]+$'
)


def parse_markdown_api(md_content: str) -> List[ApiEndpoint]:
    """
    Parse a Markdown interface definition document into a list of ApiEndpoint objects.
    """
    endpoints = []
    # Split by "## N." headings (interface sections)
    sections = re.split(r'\n(?=##\s+\d+\.)', md_content)

    for section in sections:
        if not section.strip():
            continue

        # Check if this is an interface section (starts with ## N.)
        if not re.match(r'^##\s+\d+\.', section):
            continue

        endpoint = ApiEndpoint(name="", url="", raw_section=section)

        # Extract interface name from heading
        heading_match = re.match(r'^##\s+\d+\.\s*(.*)', section)
        if heading_match:
            endpoint.name = heading_match.group(1).strip()

        # Extract URL from basic info table
        url_match = re.search(r'\|\s*URL\s*\|\s*`?([^`|\n]+)`?\s*\|', section)
        if url_match:
            endpoint.url = url_match.group(1).strip()

        # Extract method
        method_match = re.search(r'\|\s*方法\s*\|\s*(\w+)\s*\|', section)
        if method_match:
            endpoint.method = method_match.group(1).strip()

        # Extract description
        desc_match = re.search(r'\|\s*描述\s*\|\s*(.+?)\s*\|', section)
        if desc_match:
            endpoint.description = desc_match.group(1).strip()

        # Extract notes
        notes_match = re.search(r'\|\s*注意事项\s*\|\s*(.+?)\s*\|', section)
        if notes_match:
            endpoint.notes = notes_match.group(1).strip()

        # Parse request parameters table
        endpoint.request_fields = _parse_field_table(section, "请求参数")

        # Parse response parameters table
        endpoint.response_fields = _parse_field_table(section, "响应参数")

        # Parse data fields table (nested under response)
        endpoint.response_data_fields = _parse_field_table(section, "data 字段")

        endpoints.append(endpoint)

    return endpoints


def _parse_field_table(section: str, table_header: str) -> List[FieldDef]:
    """Parse a parameter table from a section."""
    fields = []

    # Find the table after the header
    # Tables start with | or || and have |---| or ||---|| separator
    pattern = rf'{re.escape(table_header)}\s*\n+(?:>.*\n)*((?:\|[^\n]+\n)+)'
    match = re.search(pattern, section)
    if not match:
        # Try alternate: just find tables near the header
        return fields

    table_text = match.group(1)
    lines = [l.strip() for l in table_text.strip().split('\n') if l.strip().startswith('|')]

    if len(lines) < 2:
        return fields

    # Skip header and separator lines
    for line in lines[2:]:  # Skip header row and separator row
        # Strip leading | or || characters, then split by |
        stripped = line.lstrip('|')
        cells = [c.strip() for c in stripped.split('|')]
        cells = [c for c in cells if c]  # Remove empty strings

        if len(cells) >= 4:
            fields.append(FieldDef(
                name=cells[0],
                data_type=cells[1],
                required=cells[2],
                description=cells[3] if len(cells) > 3 else "",
                reference=cells[4] if len(cells) > 4 else "",
            ))
        elif len(cells) >= 2:
            fields.append(FieldDef(
                name=cells[0],
                data_type=cells[1] if len(cells) > 1 else "",
                required=cells[2] if len(cells) > 2 else "",
                description=cells[3] if len(cells) > 3 else "",
                reference=cells[4] if len(cells) > 4 else "",
            ))

    return fields


def load_field_library(json_path: str) -> dict:
    """Load the company standard field library JSON."""
    if not json_path or not os.path.exists(json_path):
        return {"categories": []}

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError, OSError) as e:
        print(f"Warning: Failed to load field library '{json_path}': {e}", file=sys.stderr)
        return {"categories": []}


def get_library_field_names(field_lib: dict) -> set:
    """Extract all field names from the field library."""
    names = set()
    for category in field_lib.get("categories", []):
        for f in category.get("fields", []):
            name = f.get("fieldName", "").strip()
            if name:
                names.add(name)
    return names


# ============================================================
# Validation Functions
# ============================================================

def validate_field_types(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-01: Field types must be in allowed set."""
    issues = []
    for fld in endpoint.request_fields + endpoint.response_fields + endpoint.response_data_fields:
        dtype = fld.data_type.strip().lower()
        if dtype and dtype not in ALLOWED_ALL_TYPES:
            issues.append(ValidationIssue(
                id="V-01",
                severity=Severity.CRITICAL,
                location=f"接口: {endpoint.name} / 字段: {fld.name}",
                message=f"字段类型 '{fld.data_type}' 不在允许的类型列表中 ({', '.join(sorted(ALLOWED_ALL_TYPES))})",
                suggestion=f"将 '{fld.data_type}' 改为允许的类型之一",
            ))
    return issues


def validate_url_format(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-02: URL format must match specification."""
    issues = []
    url = endpoint.url.strip()
    if not url:
        issues.append(ValidationIssue(
            id="V-02",
            severity=Severity.CRITICAL,
            location=f"接口: {endpoint.name}",
            message="URL为空",
        ))
        return issues

    # Remove schema and host, keep only the path
    path = url
    if "://" in url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path = parsed.path
        except Exception:
            pass

    if not URL_PATTERN.match(path):
        issues.append(ValidationIssue(
            id="V-02",
            severity=Severity.CRITICAL,
            location=f"接口: {endpoint.name}",
            message=f"URL格式不符合规范: {url}",
            suggestion="URL格式应为: /openAPI/{ServiceURI}/v{N}/{Resource}[/{Child-Resource}]/{Action}",
        ))
    return issues


def validate_url_camel_case(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-03: URL path segments must be lowerCamelCase."""
    issues = []
    url = endpoint.url.strip()
    if not url:
        return issues

    # Extract path segments
    path = url
    if "://" in url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path = parsed.path
        except Exception:
            pass

    segments = [s for s in path.split("/") if s]
    # Skip openAPI, version (v1, v2...), and ServiceURI segments
    for seg in segments:
        if seg == "openAPI" or seg in SERVICE_URI_LIST or re.match(r'^v\d+$', seg):
            continue
        if not LOWER_CAMEL_RE.match(seg):
            issues.append(ValidationIssue(
                id="V-03",
                severity=Severity.CRITICAL,
                location=f"接口: {endpoint.name} / URL段: {seg}",
                message=f"URL路径段 '{seg}' 不符合小驼峰命名规范",
                suggestion=f"改为小驼峰格式，仅使用英文字母和数字",
            ))
    return issues


def validate_http_method(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-04: HTTP method must be POST."""
    if endpoint.method.upper() != "POST":
        return [ValidationIssue(
            id="V-04",
            severity=Severity.CRITICAL,
            location=f"接口: {endpoint.name}",
            message=f"HTTP方法为 '{endpoint.method}'，必须使用 POST",
            suggestion="将方法改为 POST",
        )]
    return []


def validate_field_camel_case(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-05: Field names must be lowerCamelCase.
    
    Nested dot-separated paths (e.g., filter.bodyFeature.gender) are structural,
    not field names — validate each segment separately.
    Array element paths with [] (e.g., list[].bodyFeature.gender) are sub-fields
    of array items and their segments should also be validated individually.
    """
    issues = []
    reserved_names = {"code", "message", "data"}
    for fld in endpoint.request_fields + endpoint.response_fields + endpoint.response_data_fields:
        name = fld.name.strip()
        if not name or name in reserved_names:
            continue
        # For dot-separated paths, validate each segment individually
        if '.' in name:
            segments = name.split('.')
            for seg in segments:
                # Remove array brackets like [0] or []
                seg = re.sub(r'\[.*?\]', '', seg).strip()
                if seg and seg not in reserved_names and not LOWER_CAMEL_RE.match(seg):
                    issues.append(ValidationIssue(
                        id="V-05",
                        severity=Severity.CRITICAL,
                        location=f"接口: {endpoint.name} / 字段路径段: {seg} (in {name})",
                        message=f"字段路径段 '{seg}' 不符合小驼峰命名规范",
                        suggestion=f"改为小驼峰格式 (如: myField)",
                    ))
            continue
        if not LOWER_CAMEL_RE.match(name):
            issues.append(ValidationIssue(
                id="V-05",
                severity=Severity.CRITICAL,
                location=f"接口: {endpoint.name} / 字段: {name}",
                message=f"字段名 '{name}' 不符合小驼峰命名规范",
                suggestion=f"改为小驼峰格式 (如: myField)",
            ))
    return issues


def validate_enum_description(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-06: Enum fields should list values in description.
    
    Skip array element sub-fields (e.g., list[].searchEngineType) — 
    these are sub-fields of array items and their enum values are already
    documented at the filter level or in the data model description.
    """
    issues = []
    enum_keywords = ["类型", "类别", "状态", "级别", "模式", "性别"]
    for fld in endpoint.request_fields + endpoint.response_data_fields:
        # Skip array element sub-field paths
        if ARRAY_ELEMENT_PATH_RE.search(fld.name):
            continue
        desc = fld.description
        name_lower = fld.name.lower()
        # Heuristic: if field name contains "type" or "status" or description contains enum keywords
        is_enum = any(kw in name_lower for kw in ["type", "status", "mode", "level", "gender"])
        if not is_enum and desc:
            is_enum = any(kw in desc for kw in enum_keywords)

        if is_enum and desc:
            # Check if description lists possible values
            has_value_list = bool(re.search(r'[（(].*[）)]|：.*$|:\s*\d', desc))
            if not has_value_list:
                issues.append(ValidationIssue(
                    id="V-06",
                    severity=Severity.WARNING,
                    location=f"接口: {endpoint.name} / 字段: {fld.name}",
                    message=f"枚举字段 '{fld.name}' 的描述中未列举可能的取值及含义",
                    suggestion="在字段描述中添加枚举取值及含义，如: '1-男, 2-女'",
                ))
    return issues


def validate_time_field_description(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-07: Time fields must specify ISO8601 format in description.
    
    Skip array element sub-fields (e.g., list[].happentime).
    """
    issues = []
    time_keywords = ["time", "date", "Time", "Date"]
    for fld in endpoint.request_fields + endpoint.response_data_fields:
        # Skip array element sub-field paths
        if ARRAY_ELEMENT_PATH_RE.search(fld.name):
            continue
        name = fld.name
        # Skip object-type fields that contain "time" in name but aren't time fields
        # (e.g., "timeRange" is an object containing startTime/endTime, not a time field itself)
        if fld.data_type.strip().lower() == "object":
            continue
        is_time = any(kw in name for kw in time_keywords)
        if is_time and fld.description:
            if "ISO8601" not in fld.description and "iso8601" not in fld.description.lower():
                if "格式" not in fld.description and "format" not in fld.description.lower():
                    issues.append(ValidationIssue(
                        id="V-07",
                        severity=Severity.WARNING,
                        location=f"接口: {endpoint.name} / 字段: {name}",
                        message=f"时间字段 '{name}' 的描述中未说明日期格式",
                        suggestion="在描述中说明格式，如: '日期时间，格式为ISO8601: 2023-01-01T15:30:05Z'",
                    ))
    return issues


def validate_response_structure(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-08: Response must include code + message, data is optional."""
    issues = []
    resp_names = {f.name.strip() for f in endpoint.response_fields}
    if "code" not in resp_names:
        issues.append(ValidationIssue(
            id="V-08",
            severity=Severity.CRITICAL,
            location=f"接口: {endpoint.name}",
            message="响应体缺少必带字段 'code'",
            suggestion="添加 code (integer) 字段",
        ))
    if "message" not in resp_names:
        issues.append(ValidationIssue(
            id="V-08",
            severity=Severity.CRITICAL,
            location=f"接口: {endpoint.name}",
            message="响应体缺少必带字段 'message'",
            suggestion="添加 message (string) 字段",
        ))
    return issues


def validate_boolean_prefix(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-09: Boolean fields must not use 'is' prefix.
    
    Skip array element sub-field paths.
    """
    issues = []
    for fld in endpoint.request_fields + endpoint.response_fields + endpoint.response_data_fields:
        # Skip array element sub-field paths
        if ARRAY_ELEMENT_PATH_RE.search(fld.name):
            continue
        name = fld.name.strip()
        if name.startswith("is") and len(name) > 2 and name[2].isupper():
            issues.append(ValidationIssue(
                id="V-09",
                severity=Severity.CRITICAL,
                location=f"接口: {endpoint.name} / 字段: {name}",
                message=f"布尔字段 '{name}' 使用了 'is' 前缀",
                suggestion=f"改为不带 'is' 前缀的名称，如: {name[2].lower()}{name[3:]}Flag",
            ))
    return issues


def validate_array_length_field(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-10: No extra array length fields.
    
    Note: 'num' fields with independent semantic meaning (e.g., searchEngineList.num
    meaning "number of servers involved") are NOT redundant. Only flag when the count
    field is clearly just len(array) with no additional semantic value.
    """
    issues = []
    field_names = [f.name.strip() for f in endpoint.request_fields + endpoint.response_data_fields]
    list_fields = [n for n in field_names if n.endswith("List")]
    for lf in list_fields:
        base = lf[:-4]  # Remove "List"
        # Check if there's a corresponding count/num field
        # But skip if the field is a nested property (e.g., searchEngineList.num — 'num' is a property of the list items' parent, not a count of list items)
        for n in field_names:
            if n.startswith(lf + "."):
                # This is a property OF the list object, not a redundant count — skip
                continue
            if n in (f"{base}Num", f"{base}Count", f"{base}Size", f"{base}Length"):
                issues.append(ValidationIssue(
                    id="V-10",
                    severity=Severity.CRITICAL,
                    location=f"接口: {endpoint.name} / 字段: {n}",
                    message=f"存在多余的数组长度字段 '{n}'，array类型自带长度属性",
                    suggestion=f"删除 '{n}' 字段",
                ))
    return issues


def validate_array_list_suffix(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-11: Array fields should use 'List' suffix.
    
    Exceptions:
    - Filter parameter arrays like 'channelIndexCodes', 'regionIndexCodes' use semantic suffixes
      (ONLY for non-batch request arrays; batch input arrays MUST use 'List' suffix)
    - Nested array fields within objects (e.g., searchEngineList.searchEngineInfo) — 
      the parent already has "List" suffix, child arrays use semantic naming
    - Skip array element sub-field paths (e.g., list[].searchEngineID with type array).
    - Response array field 'list' is conventional for search results.
    """
    issues = []
    # Filter array patterns that use semantic suffixes instead of 'List' (only for filter conditions)
    filter_array_patterns = re.compile(r'(IndexCodes|Codes|Ids|Keys)$', re.IGNORECASE)
    # Pattern for nested array fields where the parent already has 'List' suffix
    nested_in_list_re = re.compile(r'^[a-zA-Z]+List\.[a-zA-Z]+$')
    # Common response array field names that are conventionally used without 'List' suffix
    conventional_array_names = {"list", "records", "items"}
    
    # Determine if this is a batch interface
    is_batch = "batch" in endpoint.url.lower() or "批量" in endpoint.description
    
    for fld in endpoint.request_fields + endpoint.response_data_fields:
        # Skip array element sub-field paths — these are inside array items, not standalone arrays
        if ARRAY_ELEMENT_PATH_RE.search(fld.name):
            continue
        if fld.data_type.strip().lower() == "array":
            if not fld.name.endswith("List"):
                # For batch interfaces, request arrays with Codes/Ids suffixes should use List instead
                # (e.g., deviceIndexCodes → deviceIndexCodeList)
                if is_batch and fld in endpoint.request_fields and filter_array_patterns.search(fld.name):
                    issues.append(ValidationIssue(
                        id="V-11",
                        severity=Severity.WARNING,
                        location=f"接口: {endpoint.name} / 字段: {fld.name}",
                        message=f"批量接口的输入数组字段 '{fld.name}' 应使用 'List' 后缀而非 'Codes/Ids' 后缀",
                        suggestion=f"改为 '{fld.name[:fld.name.rfind('Codes')] + 'CodeList' if 'Codes' in fld.name else fld.name + 'List'}'",
                    ))
                    continue
                # For non-batch filter arrays, Codes/Ids suffixes are acceptable
                if filter_array_patterns.search(fld.name):
                    continue  # Acceptable semantic suffix for filter arrays
                # Check if it's a nested array within a List-parented object
                if nested_in_list_re.match(fld.name):
                    continue  # Parent already has List suffix
                # Check if it's a conventional response array name
                if fld.name.strip() in conventional_array_names:
                    continue  # Acceptable conventional name
                issues.append(ValidationIssue(
                    id="V-11",
                    severity=Severity.WARNING,
                    location=f"接口: {endpoint.name} / 字段: {fld.name}",
                    message=f"数组字段 '{fld.name}' 未使用 'List' 后缀",
                    suggestion=f"改为 '{fld.name}List'",
                ))
    return issues


def validate_service_uri(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-12: ServiceURI must be from the vocabulary list."""
    issues = []
    url = endpoint.url.strip()
    if not url:
        return issues

    path = url
    if "://" in url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path = parsed.path
        except Exception:
            pass

    segments = [s for s in path.split("/") if s]
    # openAPI is at index 0, ServiceURI at index 1
    if len(segments) >= 2 and segments[0] == "openAPI":
        service_uri = segments[1]
        if service_uri not in SERVICE_URI_LIST:
            issues.append(ValidationIssue(
                id="V-12",
                severity=Severity.CRITICAL,
                location=f"接口: {endpoint.name}",
                message=f"ServiceURI '{service_uri}' 不在规范用词列表中",
                suggestion=f"使用规范中的ServiceURI: {', '.join(SERVICE_URI_LIST)}",
            ))
    return issues


def validate_action_vocabulary(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-13: Action must be from the vocabulary list."""
    issues = []
    url = endpoint.url.strip()
    if not url:
        return issues

    path = url
    if "://" in url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            path = parsed.path
        except Exception:
            pass

    segments = [s for s in path.split("/") if s]
    if segments:
        action = segments[-1]
        if action not in ACTION_LIST and not LOWER_CAMEL_RE.match(action):
            # Only flag if it doesn't look like a valid camelCase action
            pass
        # For compound actions like searchByTimeRange, check the base action
        base_action = re.match(r'^([a-z]+)', action)
        if base_action:
            root = base_action.group(1)
            # Allow compound names that start with a known action
            known_roots = set(ACTION_LIST)
            if root not in known_roots and action not in known_roots:
                issues.append(ValidationIssue(
                    id="V-13",
                    severity=Severity.WARNING,
                    location=f"接口: {endpoint.name}",
                    message=f"Action '{action}' 不在规范用词列表中",
                    suggestion=f"建议从规范用词表中选取: {', '.join(ACTION_LIST)}",
                ))
    return issues


def validate_no_null_values(md_content: str) -> List[ValidationIssue]:
    """V-14: No null values in response examples."""
    issues = []
    # Find JSON code blocks and check for null values
    json_blocks = re.findall(r'```json\s*\n(.*?)```', md_content, re.DOTALL)
    for block in json_blocks:
        if ': null' in block or ':null' in block:
            issues.append(ValidationIssue(
                id="V-14",
                severity=Severity.CRITICAL,
                location="响应示例",
                message="响应示例中包含 null 值，规范要求不能返回 null",
                suggestion="将 null 替换为空字符串 \"\" 或删除该可选字段",
            ))
    return issues


def validate_optional_field_description(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """V-15: Optional fields should explain when to include.
    
    Skip array element sub-fields (e.g., list[].channelName) — 
    these are sub-fields of array items and their optionality is governed
    by the parent array field, not individually.
    """
    issues = []
    for fld in endpoint.request_fields:
        # Skip array element sub-field paths
        if ARRAY_ELEMENT_PATH_RE.search(fld.name):
            continue
        req = fld.required.strip()
        if req == "否" or req.lower() == "no" or req.lower() == "false":
            desc = fld.description
            # Check if description explains when/whether to include the field
            condition_keywords = ["时", "条件", "when", "不传则", "不传时", "按需", "省略", "默认值"]
            has_condition = desc and any(kw in desc for kw in condition_keywords)
            if not has_condition:
                issues.append(ValidationIssue(
                    id="V-15",
                    severity=Severity.WARNING,
                    location=f"接口: {endpoint.name} / 字段: {fld.name}",
                    message=f"可选字段 '{fld.name}' 未说明携带条件",
                    suggestion="在描述中说明什么条件下需要携带该字段",
                ))
    return issues


# ============================================================
# Business Logic Validation
# ============================================================

def validate_pagination(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """B-01: List/search interfaces should include pageNo/pageSize."""
    issues = []
    url_lower = endpoint.url.lower()
    is_list = "search" in url_lower or "list" in url_lower or "query" in url_lower

    if is_list:
        req_names = {f.name.strip() for f in endpoint.request_fields}
        resp_names = {f.name.strip() for f in endpoint.response_data_fields}

        missing = []
        if "pageNo" not in req_names:
            missing.append("pageNo")
        if "pageSize" not in req_names:
            missing.append("pageSize")

        if missing:
            issues.append(ValidationIssue(
                id="B-01",
                severity=Severity.WARNING,
                location=f"接口: {endpoint.name}",
                message=f"分页查询接口缺少分页参数: {', '.join(missing)}",
                suggestion=f"添加分页参数: {', '.join(missing)}",
            ))
    return issues


def validate_batch_response(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """B-02: Batch interfaces should use successList/failureList.
    
    Detects batch interfaces by:
    1. URL containing "batch"
    2. Description containing "批量"
    3. Request has an array parameter and response has successList/failureList pattern (partial)
    """
    issues = []
    url_lower = endpoint.url.lower()
    is_batch = "batch" in url_lower or "批量" in endpoint.description

    # Also check if the request has array input and response already has partial batch format
    req_array_fields = [f for f in endpoint.request_fields if f.data_type.strip().lower() == "array"]
    data_names = {f.name.strip() for f in endpoint.response_data_fields}
    has_partial_batch = ("successList" in data_names or "failureList" in data_names)
    
    if not is_batch and req_array_fields and has_partial_batch:
        is_batch = True  # It's a batch interface even without explicit "batch" in URL

    if is_batch:
        missing = []
        if "successList" not in data_names:
            missing.append("successList")
        if "failureList" not in data_names:
            missing.append("failureList")

        if missing:
            issues.append(ValidationIssue(
                id="B-02",
                severity=Severity.CRITICAL,
                location=f"接口: {endpoint.name}",
                message=f"批量接口响应缺少: {', '.join(missing)}",
                suggestion=f"使用 successList/failureList 格式",
            ))
    return issues


def validate_batch_seq_no(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """B-03: Batch without business codes should use seqNo."""
    # This is a suggestion, hard to detect automatically
    return []


def validate_root_index_code(md_content: str) -> List[ValidationIssue]:
    """B-04: Root IndexCode should be '1', parent should be '-1'."""
    issues = []
    # Check for parentIndexCode: null or parentIndexCode: ""
    if re.search(r'parentIndexCode["\s:]+null', md_content):
        issues.append(ValidationIssue(
            id="B-04",
            severity=Severity.CRITICAL,
            location="响应示例",
            message="根节点的父节点 IndexCode 使用了 null，应为 '-1'",
            suggestion="将 parentIndexCode 的值改为 '-1'",
        ))
    return issues


def validate_file_upload(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """B-05: File upload should use multipart/form-data."""
    issues = []
    if "upload" in endpoint.url.lower() or "导入" in endpoint.description or "import" in endpoint.url.lower():
        # Check notes or description for multipart/form-data
        all_text = endpoint.notes + endpoint.description
        if "multipart" not in all_text.lower():
            issues.append(ValidationIssue(
                id="B-05",
                severity=Severity.WARNING,
                location=f"接口: {endpoint.name}",
                message="文件上传/导入接口未说明使用 multipart/form-data",
                suggestion="在注意事项中说明使用 multipart/form-data (RFC1867) 上传",
            ))
    return issues


def validate_date_format(md_content: str) -> List[ValidationIssue]:
    """B-06: Date values should conform to ISO8601."""
    issues = []
    # Find date-like patterns that don't match ISO8601
    bad_dates = re.findall(r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}', md_content)
    if bad_dates:
        issues.append(ValidationIssue(
            id="B-06",
            severity=Severity.WARNING,
            location="文档内容",
            message=f"发现非ISO8601格式的日期: {bad_dates[0]}",
            suggestion="日期格式应为 ISO8601: 2023-01-01T15:30:05Z",
        ))
    return issues


# ============================================================
# Field Consistency Validation
# ============================================================

def validate_field_consistency(endpoints: List[ApiEndpoint], field_lib: dict) -> List[ValidationIssue]:
    """F-01/F-02: Check field names against company standard field library."""
    issues = []
    lib_names = get_library_field_names(field_lib)

    if not lib_names:
        # No field library available, skip
        return issues

    for endpoint in endpoints:
        all_fields = endpoint.request_fields + endpoint.response_fields + endpoint.response_data_fields
        for fld in all_fields:
            name = fld.name.strip()
            if not name or name in {"code", "message", "data"}:
                continue
            if name not in lib_names:
                issues.append(ValidationIssue(
                    id="F-01",
                    severity=Severity.WARNING,
                    location=f"接口: {endpoint.name} / 字段: {name}",
                    message=f"字段 '{name}' 不在公司标准字段库中",
                    suggestion="请确认字段名称是否正确，或提交修订提案添加该字段",
                ))

    return issues


# ============================================================
# Field Standard Reference Validation
# ============================================================

def validate_reference_not_empty(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """R-01: '字段标准引用' column must not be empty for each field."""
    issues = []
    reserved_names = {"code", "message", "data"}
    for fld in endpoint.request_fields + endpoint.response_fields + endpoint.response_data_fields:
        name = fld.name.strip()
        if not name or name in reserved_names:
            continue
        # Skip array element sub-field paths
        if ARRAY_ELEMENT_PATH_RE.search(name):
            continue
        # Skip dot-separated structural paths (e.g., filter.timeRange.startTime)
        if '.' in name:
            continue
        ref = fld.reference.strip()
        if not ref:
            issues.append(ValidationIssue(
                id="R-01",
                severity=Severity.WARNING,
                location=f"接口: {endpoint.name} / 字段: {name}",
                message=f"字段 '{name}' 的'字段标准引用'列为空，每个字段必须填写引用来源",
                suggestion="填写标准字段名、附录编号、'通用字段' 或 '未定义'",
            ))
    return issues


def validate_undefined_reference(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """R-02: Fields marked as '未定义' should be flagged for revision proposal."""
    issues = []
    reserved_names = {"code", "message", "data"}
    for fld in endpoint.request_fields + endpoint.response_fields + endpoint.response_data_fields:
        name = fld.name.strip()
        if not name or name in reserved_names:
            continue
        # Skip array element sub-field paths
        if ARRAY_ELEMENT_PATH_RE.search(name):
            continue
        ref = fld.reference.strip()
        if ref == "未定义":
            issues.append(ValidationIssue(
                id="R-02",
                severity=Severity.WARNING,
                location=f"接口: {endpoint.name} / 字段: {fld.name.strip()}",
                message=f"字段 '{fld.name.strip()}' 标记为'未定义'，建议提交修订提案",
                suggestion="先提交修订提案，待提案通过后再进行字段定义",
            ))
    return issues


def validate_enum_reference(endpoint: ApiEndpoint) -> List[ValidationIssue]:
    """R-03: Enum fields' reference must point to a specific standard field or appendix number."""
    issues = []
    enum_keywords = ["类型", "类别", "状态", "级别", "模式", "性别"]
    for fld in endpoint.request_fields + endpoint.response_data_fields:
        # Skip array element sub-field paths
        if ARRAY_ELEMENT_PATH_RE.search(fld.name):
            continue
        # Skip dot-separated structural paths
        if '.' in fld.name:
            continue
        desc = fld.description
        name_lower = fld.name.lower()
        # Heuristic: if field name contains "type" or "status" or description contains enum keywords
        is_enum = any(kw in name_lower for kw in ["type", "status", "mode", "level", "gender"])
        if not is_enum and desc:
            is_enum = any(kw in desc for kw in enum_keywords)

        if is_enum:
            ref = fld.reference.strip()
            # Enum fields should reference a specific standard or appendix, not just "未定义" or empty
            if not ref or ref == "未定义" or ref == "通用字段":
                issues.append(ValidationIssue(
                    id="R-03",
                    severity=Severity.WARNING,
                    location=f"接口: {endpoint.name} / 字段: {fld.name.strip()}",
                    message=f"枚举字段 '{fld.name.strip()}' 的引用'{ref}'未指向具体标准定义",
                    suggestion="枚举字段的引用应指向《服务器产品数据项标准》中具体字段或附录编号",
                ))
    return issues


# ============================================================
# Main Validation
# ============================================================

def validate_all(md_content: str, field_lib: dict) -> List[ValidationIssue]:
    """Run all validations and return the complete issue list."""
    all_issues = []

    # Parse endpoints
    endpoints = parse_markdown_api(md_content)
    if not endpoints:
        all_issues.append(ValidationIssue(
            id="PARSE",
            severity=Severity.CRITICAL,
            location="文档",
            message="未能从Markdown文档中解析出任何接口定义",
            suggestion="请检查文档格式是否符合模板要求",
        ))
        return all_issues

    # A. Specification compliance validation
    for ep in endpoints:
        all_issues.extend(validate_field_types(ep))
        all_issues.extend(validate_url_format(ep))
        all_issues.extend(validate_url_camel_case(ep))
        all_issues.extend(validate_http_method(ep))
        all_issues.extend(validate_field_camel_case(ep))
        all_issues.extend(validate_enum_description(ep))
        all_issues.extend(validate_time_field_description(ep))
        all_issues.extend(validate_response_structure(ep))
        all_issues.extend(validate_boolean_prefix(ep))
        all_issues.extend(validate_array_length_field(ep))
        all_issues.extend(validate_array_list_suffix(ep))
        all_issues.extend(validate_service_uri(ep))
        all_issues.extend(validate_action_vocabulary(ep))
        all_issues.extend(validate_optional_field_description(ep))

    # Document-level checks
    all_issues.extend(validate_no_null_values(md_content))
    all_issues.extend(validate_root_index_code(md_content))
    all_issues.extend(validate_date_format(md_content))

    # B. Business logic validation
    for ep in endpoints:
        all_issues.extend(validate_pagination(ep))
        all_issues.extend(validate_batch_response(ep))
        all_issues.extend(validate_batch_seq_no(ep))
        all_issues.extend(validate_file_upload(ep))

    # C. Field consistency validation
    all_issues.extend(validate_field_consistency(endpoints, field_lib))

    # D. Field standard reference validation
    for ep in endpoints:
        all_issues.extend(validate_reference_not_empty(ep))
        all_issues.extend(validate_undefined_reference(ep))
        all_issues.extend(validate_enum_reference(ep))

    return all_issues


def format_report(issues: List[ValidationIssue]) -> str:
    """Format validation issues into a readable report."""
    if not issues:
        return "✅ 校验通过！所有检查项均符合规范。"

    # Group by severity
    critical = [i for i in issues if i.severity == Severity.CRITICAL]
    warning = [i for i in issues if i.severity == Severity.WARNING]
    info = [i for i in issues if i.severity == Severity.INFO]

    lines = []
    lines.append(f"校验结果: 共 {len(issues)} 个问题")
    lines.append(f"  🔴 必须修正: {len(critical)}")
    lines.append(f"  🟡 建议修正: {len(warning)}")
    lines.append(f"  ℹ️  信息: {len(info)}")
    lines.append("")

    if critical:
        lines.append("--- 🔴 必须修正 ---")
        for i, issue in enumerate(critical, 1):
            lines.append(f"{i}. [{issue.id}] {issue.location}")
            lines.append(f"   问题: {issue.message}")
            if issue.suggestion:
                lines.append(f"   建议: {issue.suggestion}")
            lines.append("")

    if warning:
        lines.append("--- 🟡 建议修正 ---")
        for i, issue in enumerate(warning, 1):
            lines.append(f"{i}. [{issue.id}] {issue.location}")
            lines.append(f"   问题: {issue.message}")
            if issue.suggestion:
                lines.append(f"   建议: {issue.suggestion}")
            lines.append("")

    if info:
        lines.append("--- ℹ️ 信息 ---")
        for i, issue in enumerate(info, 1):
            lines.append(f"{i}. [{issue.id}] {issue.location}")
            lines.append(f"   {issue.message}")
            lines.append("")

    return "\n".join(lines)


def to_json_report(issues: List[ValidationIssue]) -> dict:
    """Convert validation issues to JSON report format."""
    return {
        "totalChecks": len(issues),
        "passed": 0,  # We only report failures
        "failed": len(issues),
        "issues": [
            {
                "id": issue.id,
                "severity": issue.severity.value,
                "location": issue.location,
                "message": issue.message,
                "suggestion": issue.suggestion,
            }
            for issue in issues
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Validate OpenAPI interface definitions against specification")
    parser.add_argument("--api-doc", required=True, help="Path to Markdown interface definition file")
    parser.add_argument("--field-lib", default=None, help="Path to field library JSON file")
    parser.add_argument("--output", default=None, help="Output path for JSON report (optional)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()

    # Read API doc
    try:
        with open(args.api_doc, "r", encoding="utf-8") as f:
            md_content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"Error: Failed to read API doc '{args.api_doc}': {e}", file=sys.stderr)
        sys.exit(1)

    # Load field library
    field_lib = load_field_library(args.field_lib) if args.field_lib else {"categories": []}

    # Run validation
    issues = validate_all(md_content, field_lib)

    # Output report
    if args.format == "json":
        report = to_json_report(issues)
        report_text = json.dumps(report, ensure_ascii=False, indent=2)
    else:
        report_text = format_report(issues)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report_text)
            print(f"Report saved to: {args.output}")
        except OSError as e:
            print(f"Error: Failed to write report to '{args.output}': {e}", file=sys.stderr)
            print(report_text)
    else:
        print(report_text)

    # Exit with error code if critical issues found
    critical_count = sum(1 for i in issues if i.severity == Severity.CRITICAL)
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == "__main__":
    main()
