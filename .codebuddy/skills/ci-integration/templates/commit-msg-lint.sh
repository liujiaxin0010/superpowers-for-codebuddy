#!/usr/bin/env bash
# commit-msg-lint.sh - validate commit messages against Conventional Commits.
#
# Purpose: GitLab CE has no Push Rules (an EE feature). The CI "verify" stage
#          runs this script instead; a failed job turns the pipeline red, and
#          with "Pipelines must succeed" the MR cannot be merged.
#
# Scope: all commits the MR source branch adds on top of the target branch.
# Rule:  each commit subject line must match <type>: <subject>
#        type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert
#        subject must be non-empty.
#
# Exit code: 0 = all pass; 1 = at least one non-compliant commit.
#
# Optional: to require an issue reference (e.g. [PROJ-123]), set REQUIRE_ISSUE_REF=1
#           and adjust ISSUE_REF_PATTERN to your team's convention.

set -euo pipefail

TYPE_PATTERN='^(feat|fix|docs|refactor|test|chore|perf|build|ci|revert)(\([^)]+\))?: .+'
REQUIRE_ISSUE_REF="${REQUIRE_ISSUE_REF:-0}"
ISSUE_REF_PATTERN='\[[A-Z]+-[0-9]+\]'

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

  if ! printf '%s' "$subject" | grep -Eq "$TYPE_PATTERN"; then
    echo "  FAIL ${short}  not <type>: <subject> -> ${subject}"
    fail=1
    continue
  fi

  if [ "$REQUIRE_ISSUE_REF" = "1" ] && ! printf '%s' "$subject" | grep -Eq "$ISSUE_REF_PATTERN"; then
    echo "  FAIL ${short}  missing issue reference -> ${subject}"
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
  echo "rule: <type>: <subject>, type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert"
  exit 1
fi

echo "commit-msg-lint: all ${checked} commit message(s) compliant."
exit 0
