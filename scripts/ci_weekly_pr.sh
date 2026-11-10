#!/usr/bin/env bash
# Branch, commit and push the weekly draft, then make sure it has a pull request. Used by weekly.yml; runnable locally.
#   scripts/ci_weekly_pr.sh 2026-11-08                 # commit on a local branch weekly/2026-11-08, push nothing
#   PUSH=1 scripts/ci_weekly_pr.sh 2026-11-08          # push the branch, then open the PR with gh if none is open
# The argument is the week's Sunday. If weekly/<sunday> already exists on origin it only checks the PR (the retry
# after a first attempt that pushed but could not open the PR). Env: BASE_BRANCH (default master), PR_TITLE_FILE,
# PR_BODY_FILE (default $RUNNER_TEMP/pr-title.txt, pr-body.md), GIT_COMMIT_NAME / GIT_COMMIT_EMAIL.
set -euo pipefail
SUN="${1:?usage: ci_weekly_pr.sh <sunday YYYY-MM-DD>}"
MON="$(date -d "$SUN -6 day" +%F)"
BRANCH="weekly/$SUN"
BASE="${BASE_BRANCH:-master}"
TMPD="${RUNNER_TEMP:-/tmp}"
TITLE_FILE="${PR_TITLE_FILE:-$TMPD/pr-title.txt}"
BODY_FILE="${PR_BODY_FILE:-$TMPD/pr-body.md}"
cd "$(dirname "$0")/.."

ident=()
[ -n "${GIT_COMMIT_NAME:-}" ] && ident+=(-c "user.name=$GIT_COMMIT_NAME")
[ -n "${GIT_COMMIT_EMAIL:-}" ] && ident+=(-c "user.email=$GIT_COMMIT_EMAIL")
title="Weekly roundup draft: $SUN"
[ -f "$TITLE_FILE" ] && title="$(head -n1 "$TITLE_FILE")"

if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
    echo "branch $BRANCH is already on origin; only the pull request is checked"
else
    git switch -q -c "$BRANCH"
    git add -- "site/content/weekly/$SUN" "site/static/charts/weekly/$MON.png" 2>/dev/null || true   # a missing path is caught below
    if git diff --cached --quiet; then
        echo "::error::nothing to commit for the week ending $SUN (no draft or chart was written)"
        exit 1
    fi
    git "${ident[@]}" commit -q -m "$title"
    echo "committed $BRANCH: $title"
    [ "${PUSH:-0}" = 1 ] && git push -q origin "$BRANCH"
fi

if [ "${PUSH:-0}" = 1 ]; then
    if [ "$(gh pr list --head "$BRANCH" --state open --json number --jq length)" != "0" ]; then
        echo "a pull request for $BRANCH is already open"
    else
        body_args=(--body "Draft weekly post for the week ending $SUN.")
        [ -f "$BODY_FILE" ] && body_args=(--body-file "$BODY_FILE")
        if ! gh pr create --base "$BASE" --head "$BRANCH" --title "$title" "${body_args[@]}"; then
            echo "::error::the branch $BRANCH is pushed but the pull request could not be opened. If GitHub says Actions may not create pull requests, enable Settings > Actions > General > Workflow permissions > 'Allow GitHub Actions to create and approve pull requests', then re-run this workflow (it reuses the branch)."
            exit 1
        fi
    fi
fi
