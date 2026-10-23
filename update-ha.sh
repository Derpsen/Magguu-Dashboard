#!/bin/sh
# Home Assistant updater, run by shell_command.magguu_dashboard_update as
# `sh /config/magguu-dashboard-update.sh` (installed copy of this file).
# Security: any HA user can call that service, so this script takes no
# arguments and reads no environment overrides. Config dir and source
# archive are fixed below; tests rewrite these two lines on a copy.
set -eu

CONFIG_DIR=/config
ARCHIVE_URL=https://github.com/Derpsen/Magguu-Dashboard/archive/refs/heads/main.tar.gz
WORK_DIR=""

cleanup() {
  if [ -n "$WORK_DIR" ] && [ -d "$WORK_DIR" ]; then
    rm -rf "$WORK_DIR"
  fi
}
trap cleanup EXIT INT TERM

mkdir -p "$CONFIG_DIR"

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
