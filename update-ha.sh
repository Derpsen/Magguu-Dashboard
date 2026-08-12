#!/bin/sh
set -eu

CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
ARCHIVE_URL="${MAGGUU_DASHBOARD_ARCHIVE_URL:-https://github.com/Derpsen/Magguu-Dashboard/archive/refs/heads/main.tar.gz}"
WORK_DIR=""

cleanup() {
  if [ -n "$WORK_DIR" ] && [ -d "$WORK_DIR" ]; then
    rm -rf "$WORK_DIR"
  fi
}
trap cleanup EXIT INT TERM

mkdir -p "$CONFIG_DIR"

if [ -n "${MAGGUU_DASHBOARD_SOURCE_DIR:-}" ]; then
  SOURCE_DIR=$MAGGUU_DASHBOARD_SOURCE_DIR
else
  WORK_DIR="$(mktemp -d "$CONFIG_DIR/.magguu-dashboard-update.XXXXXX")"
  ARCHIVE="$WORK_DIR/dashboard.tar.gz"
  curl -fL --retry 3 --connect-timeout 15 "$ARCHIVE_URL" -o "$ARCHIVE"
  tar -xzf "$ARCHIVE" -C "$WORK_DIR"
  SOURCE_DIR="$(find "$WORK_DIR" -mindepth 1 -maxdepth 1 -type d -name 'Magguu-Dashboard-*' | head -n 1)"
fi

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
