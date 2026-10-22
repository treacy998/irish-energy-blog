#!/usr/bin/env bash
# Commit one generated daily (post, charts, manifest) and optionally push. Used by daily.yml; runnable locally.
#   scripts/ci_publish.sh 2026-10-09          # commit only
#   PUSH=1 scripts/ci_publish.sh 2026-10-09   # commit, rebase on the remote branch, push
# Commits nothing when the paths have no changes, so a rerun is a true no-op.
set -euo pipefail
D="${1:?usage: ci_publish.sh YYYY-MM-DD}"
cd "$(dirname "$0")/.."
BRANCH="${GITHUB_REF_NAME:-$(git branch --show-current)}"

git add -- "site/content/daily/$D" "site/static/charts/$D" pipeline/data-manifest.sha256
if git diff --cached --quiet; then
    echo "no changes to commit for $D"
    exit 0
fi
git -c user.name="${GIT_COMMIT_NAME:-github-actions[bot]}" \
    -c user.email="${GIT_COMMIT_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}" \
    commit -q -m "Daily briefing $D (CI)"
echo "committed daily briefing $D"
if [ "${PUSH:-0}" = 1 ]; then
    git pull --rebase origin "$BRANCH"
    git push origin "HEAD:$BRANCH"
fi
