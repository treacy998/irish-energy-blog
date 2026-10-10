#!/usr/bin/env bash
# Tests for nightly.sh. Run: bash scripts/test_nightly.sh   (everything under a mktemp dir; the
# Python run is a stub, so no network and the real data/history.db is never touched)
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NIGHTLY="$HERE/nightly.sh"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
fail=0; n=0
ok()   { n=$((n+1)); echo "ok $1"; }
bad()  { n=$((n+1)); fail=$((fail+1)); echo "FAIL $1: $2"; }
mode() { stat -c %a "$1"; }

# Stub "python": records whether the DB is writable while it runs; STUB_EXIT / STUB_KILL steer it.
cat > "$T/stub.sh" <<'STUB'
#!/usr/bin/env bash
db=""; while [ $# -gt 0 ]; do [ "$1" = "--db" ] && db="$2"; shift; done
if [ -w "$db" ]; then echo "STUB db-writable=yes mode=$(stat -c %a "$db")"; else echo "STUB db-writable=no"; fi
echo "STUB args ok"
[ "${STUB_KILL:-}" = 1 ] && { kill -TERM "$PPID"; sleep 1; }
exit "${STUB_EXIT:-0}"
STUB
chmod +x "$T/stub.sh"

fresh() {   # fresh <name>: a clean sandbox with a read-only dummy database
    D="$T/$1"; mkdir -p "$D/backups"
    printf 'sqlite-ish bytes' > "$D/history.db"; chmod 444 "$D/history.db"
    export HISTORY_DB="$D/history.db" BACKUP_DIR="$D/backups" LOG_DIR="$D/logs" LOCK_FILE="$D/lock" NIGHTLY_PYTHON="$T/stub.sh"
    unset STUB_EXIT STUB_KILL
}
month="$(TZ=Europe/Dublin date +%Y-%m)"; today="$(TZ=Europe/Dublin date +%Y-%m-%d)"

# 1. normal run: writable only during the run, 444 after, dated backup, log written
fresh a; bash "$NIGHTLY"; rc=$?
[ $rc -eq 0 ] && ok "exit 0" || bad "exit 0" "rc=$rc"
grep -q "STUB db-writable=yes mode=644" "$D/logs/nightly-$month.log" && ok "db 644 during the run" || bad "db 644 during the run" "$(cat "$D/logs/nightly-$month.log")"
[ "$(mode "$D/history.db")" = 444 ] && ok "db 444 after" || bad "db 444 after" "$(mode "$D/history.db")"
cmp -s "$D/history.db" "$D/backups/history-$today.db" && ok "dated backup is identical" || bad "dated backup" "$(ls "$D/backups")"

# 2. the Python run fails: its exit code comes through and the DB is locked again
fresh b; STUB_EXIT=2 bash "$NIGHTLY"; rc=$?
[ $rc -eq 2 ] && [ "$(mode "$D/history.db")" = 444 ] && ok "failing run: rc passed through, db 444" || bad "failing run" "rc=$rc mode=$(mode "$D/history.db")"

# 3. the script is killed mid-run: the trap still locks the DB
fresh c; STUB_KILL=1 bash "$NIGHTLY"; rc=$?
[ $rc -eq 143 ] && [ "$(mode "$D/history.db")" = 444 ] && ok "SIGTERM mid-run: db 444" || bad "SIGTERM mid-run" "rc=$rc mode=$(mode "$D/history.db")"

# 4. overlap: a held lock stops the second run before it touches the DB
fresh d; flock "$LOCK_FILE" sleep 3 & sleep 0.5
bash "$NIGHTLY"; rc=$?; wait
[ $rc -eq 75 ] && ok "overlap exits 75" || bad "overlap exits 75" "rc=$rc"
[ "$(mode "$D/history.db")" = 444 ] && ! grep -q STUB "$D/logs/nightly-$month.log" && ok "overlap: stub not run, db untouched" || bad "overlap" "$(cat "$D/logs/nightly-$month.log")"

# 5. retention: 14 dated backups kept, other files untouched, second run the same day keeps the first copy
fresh e
for i in $(seq -w 1 20); do echo "old$i" > "$D/backups/history-2026-09-$i.db"; done
echo keep > "$D/backups/history-pre-utc-2026-10-05-1618.db"; echo keep > "$D/backups/notes.txt"
bash "$NIGHTLY"; cnt=$(ls "$D/backups"/history-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].db | wc -l)
[ "$cnt" = 14 ] && ok "14 dated backups kept" || bad "14 dated backups kept" "$cnt: $(ls "$D/backups")"
[ -e "$D/backups/history-pre-utc-2026-10-05-1618.db" ] && [ -e "$D/backups/notes.txt" ] && [ ! -e "$D/backups/history-2026-09-01.db" ] && [ -e "$D/backups/history-$today.db" ] \
    && ok "oldest pruned, others untouched" || bad "prune scope" "$(ls "$D/backups")"
chmod 644 "$D/history.db"; echo changed > "$D/history.db"; chmod 444 "$D/history.db"
bash "$NIGHTLY"; cmp -s "$D/backups/history-$today.db" "$D/history.db" && bad "retry keeps pre-update backup" "backup was replaced" || ok "retry keeps the day's first backup"

# 6. no database: exit 2, nothing created
fresh f; rm -f "$D/history.db"; bash "$NIGHTLY"; rc=$?
[ $rc -eq 2 ] && [ ! -e "$D/history.db" ] && ok "missing db exits 2" || bad "missing db" "rc=$rc"

echo "$((n-fail)) of $n passed"; [ $fail -eq 0 ]
