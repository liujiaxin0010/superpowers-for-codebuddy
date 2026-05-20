# commit-msg-lint.ps1 - validate commit messages against the accepted formats.
#
# Purpose: GitLab CE has no Push Rules (an EE feature). The CI "verify" stage
#          runs this script instead; a failed job turns the pipeline red, and
#          with "Pipelines must succeed" the MR cannot be merged.
#          Also usable for local self-check on a Windows runner.
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
#   REQUIRE_TICKET=1  accept only the ticket format, reject conventional.
#   TICKET_PATTERN    override the ticket regex; default matches AC<digits>.
#
# Note: this file is intentionally ASCII-only. Windows PowerShell 5.1 decodes a
#       BOM-less UTF-8 .ps1 with the system ANSI codepage, which corrupts non-ASCII
#       text. Keep this script ASCII-only.

$ErrorActionPreference = 'Stop'

$TypePattern = '^(feat|fix|docs|refactor|test|chore|perf|build|ci|revert)(\([^)]+\))?: .+'
$TicketPattern = if ($env:TICKET_PATTERN) { $env:TICKET_PATTERN } else { '^AC[0-9]+: .+' }
$RequireTicket = if ($env:REQUIRE_TICKET) { $env:REQUIRE_TICKET } else { '0' }

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

    $ok = $false
    if ($subject -match $TicketPattern) {
        $ok = $true
    } elseif ($RequireTicket -ne '1' -and $subject -match $TypePattern) {
        $ok = $true
    }

    if (-not $ok) {
        if ($RequireTicket -eq '1') {
            Write-Host "  FAIL $short  expected 'AC<digits>: <subject>' -> $subject"
        } else {
            Write-Host "  FAIL $short  expected 'AC<digits>:' or '<type>:' subject -> $subject"
        }
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
    if ($RequireTicket -eq '1') {
        Write-Host "accepted (REQUIRE_TICKET=1): 'AC<digits>: <subject>'"
    } else {
        Write-Host "accepted: 'AC<digits>: <subject>'  or  '<type>: <subject>'"
        Write-Host '  type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert'
    }
    exit 1
}

Write-Host "commit-msg-lint: all $checked commit message(s) compliant."
exit 0
