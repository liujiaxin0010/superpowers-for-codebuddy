#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"

TEST_REPORT_PATH="docs/quality/test-summary.json"
DOC_SYNC_PATH="docs/quality/doc-sync-report.json"
PROGRESS_PATH="docs/progress.md"
FINDINGS_PATH="docs/findings.md"
PASS_RATE_THRESHOLD="100"
COVERAGE_THRESHOLD="80"
OUTPUT_PATH="docs/quality/last-quality-gate.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --test-report)
      TEST_REPORT_PATH="$2"; shift 2 ;;
    --doc-sync)
      DOC_SYNC_PATH="$2"; shift 2 ;;
    --progress)
      PROGRESS_PATH="$2"; shift 2 ;;
    --findings)
      FINDINGS_PATH="$2"; shift 2 ;;
    --pass-rate-threshold)
      PASS_RATE_THRESHOLD="$2"; shift 2 ;;
    --coverage-threshold)
      COVERAGE_THRESHOLD="$2"; shift 2 ;;
    --output)
      OUTPUT_PATH="$2"; shift 2 ;;
    *)
      echo "未知参数: $1"
      exit 2 ;;
  esac
done

resolve_path() {
  local p="$1"
  if [[ "$p" = /* ]]; then
    printf '%s' "$p"
  else
    printf '%s/%s' "$ROOT" "$p"
  fi
}

extract_number() {
  local file="$1"
  local key="$2"
  grep -Eo "\"${key}\"[[:space:]]*:[[:space:]]*[0-9]+([.][0-9]+)?" "$file" \
    | head -n1 \
    | grep -Eo "[0-9]+([.][0-9]+)?"
}

extract_text() {
  local file="$1"
  local key="$2"
  grep -Eo "\"${key}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" "$file" \
    | head -n1 \
    | sed -E "s/.*:[[:space:]]*\"([^\"]*)\"/\1/"
}

is_lt() {
  awk -v a="$1" -v b="$2" 'BEGIN { exit !(a < b) }'
}

missing=()
failed=()
pass_rate=""
coverage=""
doc_sync_state="unknown"

test_abs="$(resolve_path "$TEST_REPORT_PATH")"
if [[ ! -f "$test_abs" ]]; then
  missing+=("test report missing: $TEST_REPORT_PATH")
else
  pass_rate="$(extract_number "$test_abs" "passRate" || true)"
  if [[ -z "$pass_rate" ]]; then
    passed="$(extract_number "$test_abs" "passed" || true)"
    total="$(extract_number "$test_abs" "total" || true)"
    if [[ -n "$passed" && -n "$total" ]] && awk -v t="$total" 'BEGIN { exit !(t > 0) }'; then
      pass_rate="$(awk -v p="$passed" -v t="$total" 'BEGIN { printf "%.4f", (p / t) * 100 }')"
    else
      failed+=("pass rate missing (need passRate or passed/total)")
    fi
  fi

  coverage="$(extract_number "$test_abs" "coverage" || true)"
  if [[ -z "$coverage" ]]; then
    coverage="$(extract_number "$test_abs" "branches" || true)"
  fi
  if [[ -z "$coverage" ]]; then
    coverage="$(extract_number "$test_abs" "statements" || true)"
  fi
  if [[ -z "$coverage" ]]; then
    failed+=("coverage missing (need coverage or branches/statements)")
  fi
fi

if [[ -n "$pass_rate" ]] && is_lt "$pass_rate" "$PASS_RATE_THRESHOLD"; then
  failed+=("pass rate ${pass_rate}% < threshold ${PASS_RATE_THRESHOLD}%")
fi
if [[ -n "$coverage" ]] && is_lt "$coverage" "$COVERAGE_THRESHOLD"; then
  failed+=("coverage ${coverage}% < threshold ${COVERAGE_THRESHOLD}%")
fi

doc_sync_abs="$(resolve_path "$DOC_SYNC_PATH")"
if [[ ! -f "$doc_sync_abs" ]]; then
  missing+=("doc sync report missing: $DOC_SYNC_PATH")
else
  status_text="$(extract_text "$doc_sync_abs" "status" || true)"
  in_sync="$(grep -Eo '"inSync"[[:space:]]*:[[:space:]]*(true|false)' "$doc_sync_abs" | head -n1 | grep -Eo '(true|false)' || true)"
  status_lower="$(printf '%s' "$status_text" | tr '[:upper:]' '[:lower:]')"
  if [[ "$in_sync" = "true" || "$status_lower" = "pass" || "$status_lower" = "ok" || "$status_lower" = "synced" ]]; then
    doc_sync_state="pass"
  else
    doc_sync_state="${status_lower:-blocked}"
    failed+=("doc sync not pass: $doc_sync_state")
  fi
fi

progress_abs="$(resolve_path "$PROGRESS_PATH")"
findings_abs="$(resolve_path "$FINDINGS_PATH")"
if [[ ! -f "$progress_abs" ]]; then
  missing+=("missing progress file: $PROGRESS_PATH")
fi
if [[ ! -f "$findings_abs" ]]; then
  missing+=("missing findings file: $FINDINGS_PATH")
fi

status="pass"
if (( ${#missing[@]} > 0 || ${#failed[@]} > 0 )); then
  status="blocked"
fi

output_abs="$(resolve_path "$OUTPUT_PATH")"
mkdir -p "$(dirname "$output_abs")"

missing_json=""
for item in "${missing[@]}"; do
  [[ -n "$missing_json" ]] && missing_json+=", "
  missing_json+="\"${item//\"/\\\"}\""
done

failed_json=""
for item in "${failed[@]}"; do
  [[ -n "$failed_json" ]] && failed_json+=", "
  failed_json+="\"${item//\"/\\\"}\""
done

checked_at="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
cat > "$output_abs" <<JSON
{
  "status": "$status",
  "checkedAt": "$checked_at",
  "passRate": ${pass_rate:-null},
  "passRateThreshold": $PASS_RATE_THRESHOLD,
  "coverage": ${coverage:-null},
  "coverageThreshold": $COVERAGE_THRESHOLD,
  "docSyncStatus": "$doc_sync_state",
  "missing": [${missing_json}],
  "failed": [${failed_json}]
}
JSON

if [[ "$status" = "blocked" ]]; then
  echo "质量门禁: BLOCKED"
  for item in "${missing[@]}"; do
    echo " - 缺失: $item"
  done
  for item in "${failed[@]}"; do
    echo " - 未达标: $item"
  done
  echo " - output: $OUTPUT_PATH"
  exit 1
fi

echo "质量门禁: PASS"
printf ' - passRate: %.2f%% (>= %.2f%%)\n' "$pass_rate" "$PASS_RATE_THRESHOLD"
printf ' - coverage: %.2f%% (>= %.2f%%)\n' "$coverage" "$COVERAGE_THRESHOLD"
echo " - docSync: pass"
echo " - output: $OUTPUT_PATH"
exit 0
