# commit-msg-lint.ps1 - validate commit messages against Conventional Commits.
#
# Purpose: GitLab CE has no Push Rules (an EE feature). The CI "verify" stage
#          runs this script instead; a failed job turns the pipeline red, and
#          with "Pipelines must succeed" the MR cannot be merged.
#          Also usable for local self-check on a Windows runner.
#
# Scope: all commits the MR source branch adds on top of the target branch.
# Rule:  each commit subject line must match <type>: <subject>
#        type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert
#        subject must be non-empty.
#
# Exit code: 0 = all pass; 1 = at least one non-compliant commit.
#
# Optional: to require an issue reference (e.g. [PROJ-123]), set env REQUIRE_ISSUE_REF=1
#           and adjust $IssueRefPattern to your team's convention.
#
# Note: this file is intentionally ASCII-only. Windows PowerShell 5.1 decodes a
#       BOM-less UTF-8 .ps1 with the system ANSI codepage, which corrupts non-ASCII
#       text. Keep this script ASCII-only.

$ErrorActionPreference = 'Stop'

$TypePattern = '^(feat|fix|docs|refactor|test|chore|perf|build|ci|revert)(\([^)]+\))?: .+'
$RequireIssueRef = if ($env:REQUIRE_ISSUE_REF) { $env:REQUIRE_ISSUE_REF } else { '0' }
$IssueRefPattern = '\[[A-Z]+-[0-9]+\]'

# Determine the commit range: prefer GitLab MR predefined variables,
# fall back to the last 20 commits (safe on shallow history).
if ($env:CI_MERGE_REQUEST_DIFF_BASE_SHA) {
    $RevArgs = @("$($env:CI_MERGE_REQUEST_DIFF_BASE_SHA)..HEAD")
} elseif ($env:CI_DEFAULT_BRANCH) {
    $RevArgs = @("origin/$($env:CI_DEFAULT_BRANCH)..HEAD")
} else {
    $RevArgs = @('--max-count=20', 'HEAD')
}

Write-Host "commit-msg-lint: range $($RevArgs -join ' ')"

$shas = @(git rev-list @RevArgs 2>$null)
$fail = $false
$checked = 0

foreach ($sha in $shas) {
    if ([string]::IsNullOrWhiteSpace($sha)) { continue }
    $checked++
    $subject = git log -1 --format=%s $sha
    $short = git log -1 --format=%h $sha

    if ($subject -notmatch $TypePattern) {
        Write-Host "  FAIL $short  not <type>: <subject> -> $subject"
        $fail = $true
        continue
    }

    if ($RequireIssueRef -eq '1' -and $subject -notmatch $IssueRefPattern) {
        Write-Host "  FAIL $short  missing issue reference -> $subject"
        $fail = $true
        continue
    }

    Write-Host "  OK   $short  $subject"
}

if ($checked -eq 0) {
    Write-Host 'commit-msg-lint: no commits in range, skipped.'
    exit 0
}

if ($fail) {
    Write-Host 'commit-msg-lint: non-compliant commit message(s) found, pipeline blocked.'
    Write-Host 'rule: <type>: <subject>, type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert'
    exit 1
}

Write-Host "commit-msg-lint: all $checked commit message(s) compliant."
exit 0
