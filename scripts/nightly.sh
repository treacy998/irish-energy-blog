#!/usr/bin/env bash
# nightly.sh — keep data/history.db current without anyone running run_daily by hand.
#
#   1. takes a lock, so a slow run and the retry never overlap
#   2. backs history.db up to ~/backups/history-YYYY-MM-DD.db (first run of the day; keeps 14)
#   3. chmod 644 the database for the run, chmod 444 again on every exit path (trap), so a crash
#      or a kill can't leave it writable (SIGKILL is the one thing a trap can't see)
#   4. run_daily.py --store-only with the venv python by full path
#   5. everything goes to logs/nightly-YYYY-MM.log (Irish calendar month)
#
# Exit code: the one run_daily.py --store-only returned (0 ok, 1 older price missing, 2 error),
# 75 if another run holds the lock, 2 if the database is missing.
#
# Test overrides (all optional): HISTORY_DB, BACKUP_DIR, LOG_DIR, LOCK_FILE, NIGHTLY_PYTHON.

set -u
export TZ=Europe/Dublin
export PATH=/usr/local/bin:/usr/bin:/bin

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB="${HISTORY_DB:-$ROOT/data/history.db}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
LOG_DIR="${LOG_DIR:-$ROOT/logs}"
LOCK_FILE="${LOCK_FILE:-/tmp/irish-energy-nightly.lock}"
PYTHON="${NIGHTLY_PYTHON:-$ROOT/venv/bin/python}"
KEEP=14

mkdir -p "$LOG_DIR" "$BACKUP_DIR"
exec >>"$LOG_DIR/nightly-$(date +%Y-%m).log" 2>&1
log() { echo "$(date '+%Y-%m-%d %H:%M:%S %Z') nightly: $*"; }

exec 9>"$LOCK_FILE"
if ! flock -n 9; then
    log "another run holds $LOCK_FILE; exiting without touching the store"
    exit 75
fi

if [ ! -f "$DB" ]; then
    log "STORE NOT WRITABLE: $DB does not exist"
    exit 2
fi

# Backup first (the mode doesn't matter for reading). One per day: the retry must not replace
# the pre-update copy with a post-update one.
dest="$BACKUP_DIR/history-$(date +%Y-%m-%d).db"
if [ -e "$dest" ]; then
    log "backup $dest already exists; keeping it"
elif cp -- "$DB" "$dest" && cmp -s -- "$DB" "$dest"; then
    log "backed up to $dest"
else
    log "BACKUP FAILED: $dest"
    rm -f -- "$dest"
    exit 2
fi
# Only the dated files this script writes; history-pre-*.db and anything else stay.
ls -1 "$BACKUP_DIR"/history-[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].db 2>/dev/null \
    | sort | head -n -"$KEEP" | while read -r old; do rm -f -- "$old" && log "pruned $old"; done

relock() { chmod 444 -- "$DB"; }
trap relock EXIT
trap 'exit 143' TERM
trap 'exit 130' INT HUP

chmod 644 -- "$DB"
log "run_daily.py --store-only --db $DB"
"$PYTHON" "$ROOT/pipeline/run_daily.py" --store-only --db "$DB"
rc=$?
log "exit $rc"
exit "$rc"
