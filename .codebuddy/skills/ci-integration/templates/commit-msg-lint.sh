#!/usr/bin/env bash
# commit-msg-lint.sh - validate commit messages against the accepted formats.
#
# Purpose: GitLab CE has no Push Rules (an EE feature). The CI "verify" stage
#          runs this script instead; a failed job turns the pipeline red, and
#          with "Pipelines must succeed" the MR cannot be merged.
#
# Scope: all commits the MR source branch adds on top of the target branch.
#
# Accepted subject formats (either one passes by default):
#   1. Ticket format       : AC<digits>: <subject>   e.g. AC44753: fix title
#   2. Conventional format : <type>: <subject>       e.g. fix: correct title
#      type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert
#
# Exit code: 0 = all pass; 1 = at least one non-compliant commit.
#
# Options (environment variables):
#   REQUIRE_TICKET=1  accept only the ticket format, reject conventional
#                     (use when every commit must carry a ticket id)
#   TICKET_PATTERN    override the ticket regex; default matches AC<digits>.
#                     For other prefixes set e.g. '^(AC|DTS)[0-9]+: .+'

set -euo pipefail

TYPE_PATTERN='^(feat|fix|docs|refactor|test|chore|perf|build|ci|revert)(\([^)]+\))?: .+'
TICKET_PATTERN="${TICKET_PATTERN:-^AC[0-9]+: .+}"
REQUIRE_TICKET="${REQUIRE_TICKET:-0}"

# Determine the commit range: prefer GitLab MR predefined variables,
# fall back to the last 20 commits (safe on shallow history).
if [ -n "${CI_MERGE_REQUEST_DIFF_BASE_SHA:-}" ]; then
  REVLIST_ARGS="${CI_MERGE_REQUEST_DIFF_BASE_SHA}..HEAD"
elif [ -n "${CI_DEFAULT_BRANCH:-}" ]; then
  REVLIST_ARGS="origin/${CI_DEFAULT_BRANCH}..HEAD"
else
  REVLIST_ARGS="--max-count=20 HEAD"
fi

echo "commit-msg-lint: range ${REVLIST_ARGS}"

fail=0
checked=0

while IFS= read -r sha; do
  [ -z "$sha" ] && continue
  checked=$((checked + 1))
  subject=$(git log -1 --format=%s "$sha")
  short=$(git log -1 --format=%h "$sha")

  ok=0
  if printf '%s' "$subject" | grep -Eq "$TICKET_PATTERN"; then
    ok=1
  elif [ "$REQUIRE_TICKET" != "1" ] && printf '%s' "$subject" | grep -Eq "$TYPE_PATTERN"; then
    ok=1
  fi

  if [ "$ok" -ne 1 ]; then
    if [ "$REQUIRE_TICKET" = "1" ]; then
      echo "  FAIL ${short}  expected 'AC<digits>: <subject>' -> ${subject}"
    else
      echo "  FAIL ${short}  expected 'AC<digits>:' or '<type>:' subject -> ${subject}"
    fi
    fail=1
    continue
  fi

  echo "  OK   ${short}  ${subject}"
done < <(git rev-list $REVLIST_ARGS 2>/dev/null || true)

if [ "$checked" -eq 0 ]; then
  echo "commit-msg-lint: no commits in range, skipped."
  exit 0
fi

if [ "$fail" -ne 0 ]; then
  echo "commit-msg-lint: non-compliant commit message(s) found, pipeline blocked."
  if [ "$REQUIRE_TICKET" = "1" ]; then
    echo "accepted (REQUIRE_TICKET=1): 'AC<digits>: <subject>'"
  else
    echo "accepted: 'AC<digits>: <subject>'  or  '<type>: <subject>'"
    echo "  type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert"
  fi
  exit 1
fi

echo "commit-msg-lint: all ${checked} commit message(s) compliant."
exit 0
