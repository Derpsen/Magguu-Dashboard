#!/bin/sh
set -eu

CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
ARCHIVE_URL="https://github.com/Derpsen/Magguu-Dashboard/archive/refs/heads/main.tar.gz"
WORK_DIR="$(mktemp -d "$CONFIG_DIR/.magguu-dashboard-update.XXXXXX")"
ARCHIVE="$WORK_DIR/dashboard.tar.gz"
BACKUP_DIR="$CONFIG_DIR/backups/magguu-dashboard-$(date +%Y%m%d-%H%M%S)"
DASHBOARD_TARGET="$CONFIG_DIR/dashboard/magguu-flux"
PACKAGE_TARGET="$CONFIG_DIR/packages/magguu_flux.yaml"
THEME_TARGET="$CONFIG_DIR/themes/magguu_midnight.yaml"
UPDATER_TARGET="$CONFIG_DIR/magguu-dashboard-update.sh"

cleanup() {
  rm -rf "$WORK_DIR"
}
trap cleanup EXIT INT TERM

curl -fL --retry 3 --connect-timeout 15 "$ARCHIVE_URL" -o "$ARCHIVE"
tar -xzf "$ARCHIVE" -C "$WORK_DIR"
SOURCE_DIR="$(find "$WORK_DIR" -mindepth 1 -maxdepth 1 -type d -name 'Magguu-Dashboard-*' | head -n 1)"

for required in dashboard/magguu-flux packages/magguu_flux.yaml themes/magguu_midnight.yaml update-ha.sh; do
  if [ ! -e "$SOURCE_DIR/$required" ]; then
    echo "Fehlende Quelldatei im Download: $required" >&2
    exit 1
  fi
done

mkdir -p "$BACKUP_DIR" "$CONFIG_DIR/dashboard" "$CONFIG_DIR/packages" "$CONFIG_DIR/themes"

if [ -d "$DASHBOARD_TARGET" ]; then
  cp -a "$DASHBOARD_TARGET" "$BACKUP_DIR/"
fi
if [ -f "$PACKAGE_TARGET" ]; then
  cp -a "$PACKAGE_TARGET" "$BACKUP_DIR/"
fi
if [ -f "$THEME_TARGET" ]; then
  cp -a "$THEME_TARGET" "$BACKUP_DIR/"
fi

rm -rf "$DASHBOARD_TARGET"
cp -a "$SOURCE_DIR/dashboard/magguu-flux" "$DASHBOARD_TARGET"
cp -a "$SOURCE_DIR/packages/magguu_flux.yaml" "$PACKAGE_TARGET"
cp -a "$SOURCE_DIR/themes/magguu_midnight.yaml" "$THEME_TARGET"
cp -a "$SOURCE_DIR/update-ha.sh" "$UPDATER_TARGET"
chmod 755 "$UPDATER_TARGET"

echo "Magguu Dashboard aktualisiert. Backup: $BACKUP_DIR"
