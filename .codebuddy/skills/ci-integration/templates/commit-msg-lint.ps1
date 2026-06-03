# commit-msg-lint.ps1 - validate commit messages against the accepted formats.
#
# Purpose: GitLab CE has no Push Rules (an EE feature). The CI "verify" stage
#          runs this script instead; a failed job turns the pipeline red, and
#          with "Pipelines must succeed" the MR cannot be merged. It also mirrors
#          the team server-side AI-tag hook so violations are caught locally first.
#          Also usable for local self-check on a Windows runner.
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
# Rule 2 - subject format (after the tag). One of the following must pass:
#            1. Ticket format       : AC<digits>: <subject>   e.g. [AI-H] AC44753: fix title
#            2. Conventional format : <type>: <subject>       e.g. [AI-100] fix: correct title
#               type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert
#
# Exit code: 0 = all pass; 1 = at least one non-compliant commit.
#
# Options (environment variables):
#   REQUIRE_TICKET=1  accept only the ticket format after the tag, reject conventional.
#   TICKET_PATTERN    override the ticket regex; default matches AC<digits>.
#
# Note: this file is intentionally ASCII-only. Windows PowerShell 5.1 decodes a
#       BOM-less UTF-8 .ps1 with the system ANSI codepage, which corrupts non-ASCII
#       text. Keep this script ASCII-only.

$ErrorActionPreference = 'Stop'

$AiTagPattern = '\[AI-(0|H|100)\]'
$AiPrefixPattern = '^\[AI-(0|H|100)\] .+'
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
    $body = (git log -1 --format=%B $sha) -join "`n"
    $short = git log -1 --format=%h $sha

    # Rule 1: exactly one AI tag in the whole message.
    $tagCount = ([regex]::Matches($body, $AiTagPattern)).Count
    if ($tagCount -eq 0) {
        Write-Host "  FAIL $short  missing AI tag; need exactly one of [AI-0] [AI-H] [AI-100] -> $subject"
        $fail = $true
        continue
    }
    if ($tagCount -gt 1) {
        Write-Host "  FAIL $short  multiple AI tags ($tagCount); only one allowed -> $subject"
        $fail = $true
        continue
    }

    # Rule 1b: the tag must be the subject prefix.
    if ($subject -notmatch $AiPrefixPattern) {
        Write-Host "  FAIL $short  AI tag must be the subject prefix, e.g. '[AI-H] <subject>' -> $subject"
        $fail = $true
        continue
    }

    # Rule 2: format of the subject after stripping the tag prefix.
    $rest = $subject -replace '^\[AI-(0|H|100)\] ', ''
    $ok = $false
    if ($rest -match $TicketPattern) {
        $ok = $true
    } elseif ($RequireTicket -ne '1' -and $rest -match $TypePattern) {
        $ok = $true
    }

    if (-not $ok) {
        if ($RequireTicket -eq '1') {
            Write-Host "  FAIL $short  expected '[AI-x] AC<digits>: <subject>' -> $subject"
        } else {
            Write-Host "  FAIL $short  expected '[AI-x] AC<digits>:' or '[AI-x] <type>:' subject -> $subject"
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
    Write-Host 'AI tag (exactly one, required as subject prefix):'
    Write-Host '  [AI-0]    hand-written code'
    Write-Host '  [AI-H]    human + AI collaboration'
    Write-Host '  [AI-100]  fully AI-generated code'
    if ($RequireTicket -eq '1') {
        Write-Host "accepted (REQUIRE_TICKET=1): '[AI-x] AC<digits>: <subject>'"
    } else {
        Write-Host "accepted: '[AI-x] AC<digits>: <subject>'  or  '[AI-x] <type>: <subject>'"
        Write-Host '  type in feat|fix|docs|refactor|test|chore|perf|build|ci|revert'
    }
    Write-Host 'example: [AI-H] AC16330 fix title   |   [AI-100] feat: add X'
    exit 1
}

Write-Host "commit-msg-lint: all $checked commit message(s) compliant."
exit 0
