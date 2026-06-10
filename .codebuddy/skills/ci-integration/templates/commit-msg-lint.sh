#!/usr/bin/env bash
# commit-msg-lint.sh - validate commit messages against the accepted formats.
# TEMPLATE_VERSION: 1.0.1  (changelog: 引擎仓库根目录 CHANGELOG.md)
#
# Purpose: GitLab CE has no Push Rules (an EE feature). The CI "verify" stage
#          runs this script instead; a failed job turns the pipeline red, and
#          with "Pipelines must succeed" the MR cannot be merged. It also mirrors
#          the team server-side AI-tag hook so violations are caught locally first.
#
# Scope: all commits the MR source branch adds on top of the target branch.
#
# Rule 1 - AI tag (required, exactly one). Every commit message MUST carry one,
#          and only one, AI tag as the subject prefix:
#            [AI-0]    hand-written code
#            [AI-H]    human + AI collaboration
#            [AI-100]  fully AI-generated code
#          Zero tags or more than one tag (anywhere in the message) is rejected.
#
# Rule 2 - subject format (after the tag). One of the following must pass
#          (either one by default):
#            1. Ticket format       : AC<digits>: <subject>
#               e.g. [AI-H] AC44753: fix title
#            2. Conventional format : <type>: <subject>
#               e.g. [AI-100] fix: correct title
#               type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert
#
# Exit code: 0 = all pass; 1 = at least one non-compliant commit.
#
# Options (environment variables):
#   REQUIRE_TICKET=1  accept only the ticket format after the tag, reject conventional
#                     (use when every commit must carry a ticket id)
#   TICKET_PATTERN    override the ticket regex; default matches AC<digits>.
#                     For other prefixes set e.g. '^(AC|DTS)[0-9]+: .+'

set -euo pipefail

AI_TAG_PATTERN='\[AI-(0|H|100)\]'
AI_PREFIX_PATTERN='^\[AI-(0|H|100)\] .+'
TYPE_PATTERN='^(feat|fix|docs|refactor|test|chore|perf|build|ci|revert)(\([^)]+\))?: .+'
TICKET_PATTERN="${TICKET_PATTERN:-^AC[0-9]+: .+}"
REQUIRE_TICKET="${REQUIRE_TICKET:-0}"

# Merge commits are skipped (--no-merges): their messages are auto-generated
# (GitLab merge trains, "Merge branch 'master' into feature", GitHub Actions'
# synthetic PR merge commit) and must not be forced to carry an AI tag.
#
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
  body=$(git log -1 --format=%B "$sha")
  short=$(git log -1 --format=%h "$sha")

  # Rule 1: exactly one AI tag in the whole message.
  tag_count=$(printf '%s\n' "$body" | { grep -oE "$AI_TAG_PATTERN" || true; } | wc -l | tr -d ' \n')
  if [ "${tag_count:-0}" -eq 0 ]; then
    echo "  FAIL ${short}  missing AI tag; need exactly one of [AI-0] [AI-H] [AI-100] -> ${subject}"
    fail=1
    continue
  fi
  if [ "$tag_count" -gt 1 ]; then
    echo "  FAIL ${short}  multiple AI tags (${tag_count}); only one allowed -> ${subject}"
    fail=1
    continue
  fi

  # Rule 1b: the tag must be the subject prefix.
  if ! printf '%s' "$subject" | grep -Eq "$AI_PREFIX_PATTERN"; then
    echo "  FAIL ${short}  AI tag must be the subject prefix, e.g. '[AI-H] <subject>' -> ${subject}"
    fail=1
    continue
  fi

  # Rule 2: format of the subject after stripping the tag prefix.
  rest=$(printf '%s' "$subject" | sed -E 's/^\[AI-(0|H|100)\] //')
  ok=0
  if printf '%s' "$rest" | grep -Eq "$TICKET_PATTERN"; then
    ok=1
  elif [ "$REQUIRE_TICKET" != "1" ] && printf '%s' "$rest" | grep -Eq "$TYPE_PATTERN"; then
    ok=1
  fi

  if [ "$ok" -ne 1 ]; then
    if [ "$REQUIRE_TICKET" = "1" ]; then
      echo "  FAIL ${short}  expected '[AI-x] AC<digits>: <subject>' -> ${subject}"
    else
      echo "  FAIL ${short}  expected '[AI-x] AC<digits>:' or '[AI-x] <type>:' subject -> ${subject}"
    fi
    fail=1
    continue
  fi

  echo "  OK   ${short}  ${subject}"
done < <(git rev-list --no-merges $REVLIST_ARGS 2>/dev/null || true)

if [ "$checked" -eq 0 ]; then
  echo "commit-msg-lint: no commits in range, skipped."
  exit 0
fi

if [ "$fail" -ne 0 ]; then
  echo "commit-msg-lint: non-compliant commit message(s) found, pipeline blocked."
  echo "AI tag (exactly one, required as subject prefix):"
  echo "  [AI-0]    hand-written code"
  echo "  [AI-H]    human + AI collaboration"
  echo "  [AI-100]  fully AI-generated code"
  if [ "$REQUIRE_TICKET" = "1" ]; then
    echo "accepted (REQUIRE_TICKET=1): '[AI-x] AC<digits>: <subject>'"
  else
    echo "accepted: '[AI-x] AC<digits>: <subject>'  or  '[AI-x] <type>: <subject>'"
    echo "  type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert"
  fi
  echo "example: [AI-H] AC16330 fix title   |   [AI-100] feat: add X"
  exit 1
fi

echo "commit-msg-lint: all ${checked} commit message(s) compliant."
exit 0
