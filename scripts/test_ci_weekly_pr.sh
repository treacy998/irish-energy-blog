#!/usr/bin/env bash
# Tests for ci_weekly_pr.sh. Run: bash scripts/test_ci_weekly_pr.sh   (a temp repo with a bare origin and a stub gh on
# PATH; no network, and the real repo is never touched)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pass=0; fail=0
ok()   { echo "ok $1"; pass=$((pass + 1)); }
bad()  { echo "FAIL $1"; fail=$((fail + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }

SUN=2026-11-08; MON=2026-11-02; BR="weekly/$SUN"

fresh() {          # a clone with the draft and chart written, plus a bare origin; sets W (work), O (origin), GH (stub dir)
    T="$(mktemp -d)"; O="$T/origin.git"; W="$T/work"; GH="$T/bin"; mkdir -p "$GH"
    git init -q --bare -b master "$O"
    git clone -q "$O" "$W" 2>/dev/null
    mkdir -p "$W/scripts" "$W/site/content/weekly/$SUN" "$W/site/static/charts/weekly"
    cp "$HERE/ci_weekly_pr.sh" "$W/scripts/"
    git -C "$W" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
    git -C "$W" push -q origin HEAD:master
    printf -- '---\ntitle: x\n---\n' > "$W/site/content/weekly/$SUN/index.md"
    printf 'png' > "$W/site/static/charts/weekly/$MON.png"
    printf 'Weekly roundup draft: 2–8 November 2026\n' > "$T/pr-title.txt"; printf 'body\n' > "$T/pr-body.md"
    cat > "$GH/gh" <<'STUB'
#!/usr/bin/env bash
echo "gh $*" >> "$GH_LOG"
case "$1 $2" in
  "pr list") echo "${GH_OPEN_PRS:-0}" ;;
  "pr create") [ -n "${GH_CREATE_FAILS:-}" ] && { echo "GraphQL: GitHub Actions is not permitted to create or approve pull requests" >&2; exit 1; }; echo "https://github.com/x/y/pull/1" ;;
esac
STUB
    chmod +x "$GH/gh"; : > "$T/gh.log"
}
run() { ( cd "$W" && env PATH="$GH:$PATH" GH_LOG="$T/gh.log" PR_TITLE_FILE="$T/pr-title.txt" PR_BODY_FILE="$T/pr-body.md" \
          GIT_COMMIT_NAME="eoin treacy" GIT_COMMIT_EMAIL="e@x.test" BASE_BRANCH=master "$@" bash scripts/ci_weekly_pr.sh "$SUN" ) > "$T/out" 2>&1; echo $? > "$T/rc"; }
on_origin() { git -C "$O" rev-parse --verify -q "refs/heads/$BR" >/dev/null; }

fresh; run PUSH=0
check "without PUSH: a local commit on weekly/<sunday>, nothing pushed, gh never called" \
  '[ "$(cat $T/rc)" = 0 ] && [ "$(git -C $W branch --show-current)" = "$BR" ] && ! on_origin && [ ! -s $T/gh.log ]'
check "the commit holds only the post and the chart, titled from the PR title file" \
  '[ "$(git -C $W show --name-only --format=%s HEAD | grep -v "^$" | tr "\n" "|")" = "Weekly roundup draft: 2–8 November 2026|site/content/weekly/$SUN/index.md|site/static/charts/weekly/$MON.png|" ]'
check "authored as the commit identity variables, no co-author trailer" \
  '[ "$(git -C $W log -1 --format=%an)" = "eoin treacy" ] && ! git -C $W log -1 --format=%B | grep -qi co-authored'

fresh; run PUSH=1
check "PUSH=1: the branch is on origin and the PR is opened against master from it with the body file" \
  'on_origin && grep -q "^gh pr create --base master --head $BR --title Weekly roundup draft: 2–8 November 2026 --body-file $T/pr-body.md" $T/gh.log'

fresh; run PUSH=1 GH_OPEN_PRS=1
check "an open PR is not duplicated" '! grep -q "pr create" $T/gh.log && grep -q "already open" $T/out'

fresh; run PUSH=1; : > "$T/gh.log"; git -C "$W" switch -q master; before="$(git -C "$O" rev-parse $BR)"; run PUSH=1
check "a rerun with the branch already on origin commits nothing and only checks for the PR" \
  '[ "$(git -C $O rev-parse $BR)" = "$before" ] && grep -q "already on origin" $T/out && grep -q "pr create" $T/gh.log'

fresh; run PUSH=1 GH_CREATE_FAILS=1
check "a refused PR fails the run, keeps the pushed branch and names the setting to enable" \
  '[ "$(cat $T/rc)" != 0 ] && on_origin && grep -q "Allow GitHub Actions to create and approve pull requests" $T/out'

fresh; rm "$W/site/content/weekly/$SUN/index.md" "$W/site/static/charts/weekly/$MON.png"; run PUSH=1
check "nothing to commit is an error, not a silent success" '[ "$(cat $T/rc)" != 0 ] && grep -q "nothing to commit" $T/out && ! on_origin'

echo "$pass of $((pass + fail)) passed"
[ "$fail" = 0 ]
