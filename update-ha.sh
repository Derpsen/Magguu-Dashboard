#!/bin/sh
# Home Assistant updater, run by shell_command.magguu_dashboard_update as
# `sh /config/magguu-dashboard-update.sh` (installed copy of this file).
# Security: any HA user can call that service, so this script takes no
# arguments and reads no environment overrides. Config dir and source
# archive are fixed below; tests rewrite these lines on a copy.
# Concurrency: only one run at a time. flock (kernel lock, released when the
# process dies) if available, otherwise an mkdir lock; an mkdir lock older
# than LOCK_STALE_SECONDS (10 min) is treated as stale and taken over.
# A second concurrent run logs one line and exits 0 without changing anything.
set -eu

CONFIG_DIR=/config
ARCHIVE_URL=https://github.com/Derpsen/Magguu-Dashboard/archive/refs/heads/main.tar.gz
LOCK_MODE=auto
LOCK_STALE_SECONDS=600
LOCK_FILE="$CONFIG_DIR/.magguu-dashboard-update.lock"
LOCK_DIR="$CONFIG_DIR/.magguu-dashboard-update.lockdir"
LOCK_HELD=""
WORK_DIR=""

# shellcheck disable=SC2329 # invoked via trap (false positive with exiting functions)
cleanup() {
  if [ -n "$WORK_DIR" ] && [ -d "$WORK_DIR" ]; then
    rm -rf "$WORK_DIR"
  fi
  if [ "$LOCK_HELD" = mkdir ]; then
    rm -rf "$LOCK_DIR"
  fi
}

trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

skip_running() {
  echo "Magguu-Dashboard-Update läuft bereits – dieser Aufruf wird übersprungen."
  exit 0
}

lock_is_stale() {
  lock_now=$(date +%s)
  if lock_mtime=$(stat -c %Y "$LOCK_DIR" 2>/dev/null); then
    [ $((lock_now - lock_mtime)) -ge "$LOCK_STALE_SECONDS" ]
    return
  fi
  [ -d "$LOCK_DIR" ] || return 0
  [ -n "$(find "$LOCK_DIR" -prune -mmin +$((LOCK_STALE_SECONDS / 60)) 2>/dev/null)" ]
}

acquire_mkdir_lock() {
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    LOCK_HELD="mkdir"
    return 0
  fi
  if ! lock_is_stale; then
    skip_running
  fi
  echo "Veraltete Update-Sperre (älter als 10 min) wird übernommen."
  rm -rf "$LOCK_DIR"
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    LOCK_HELD="mkdir"
    return 0
  fi
  skip_running
}

acquire_flock() {
  exec 9>"$LOCK_FILE"
  if ! flock -n 9; then
    skip_running
  fi
  LOCK_HELD="flock"
}

main() {
  mkdir -p "$CONFIG_DIR"
  if [ "$LOCK_MODE" = auto ] && command -v flock >/dev/null 2>&1; then
    acquire_flock
  else
    acquire_mkdir_lock
  fi

  WORK_DIR="$(mktemp -d "$CONFIG_DIR/.magguu-dashboard-update.XXXXXX")"
  ARCHIVE="$WORK_DIR/dashboard.tar.gz"
  curl -fL --retry 3 --connect-timeout 15 "$ARCHIVE_URL" -o "$ARCHIVE"
  tar -xzf "$ARCHIVE" -C "$WORK_DIR"
  SOURCE_DIR="$(find "$WORK_DIR" -mindepth 1 -maxdepth 1 -type d -name 'Magguu-Dashboard-*' | head -n 1)"

  if [ -z "$SOURCE_DIR" ] || [ ! -d "$SOURCE_DIR" ]; then
    echo "Dashboard-Quellverzeichnis wurde nicht gefunden." >&2
    exit 1
  fi

  INSTALLER="$SOURCE_DIR/scripts/install-dashboard.sh"
  if [ ! -f "$INSTALLER" ]; then
    echo "Fehlende Quelldatei: $INSTALLER" >&2
    exit 1
  fi

  # shellcheck source=scripts/install-dashboard.sh
  . "$INSTALLER"
  magguu_install_dashboard "$SOURCE_DIR" "$CONFIG_DIR"

  echo "Magguu Dashboard aktualisiert. Backup: $MAGGUU_BACKUP_DIR"
}

# main and exit on one line: the shell parses it before running, so the
# installer overwriting this very file mid-run cannot inject new commands.
main; exit $?
