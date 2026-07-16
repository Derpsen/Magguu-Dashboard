#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
DASHBOARD_TARGET="$CONFIG_DIR/dashboard/magguu-flux"
PACKAGE_TARGET="$CONFIG_DIR/packages/magguu_flux.yaml"
THEME_TARGET="$CONFIG_DIR/themes/magguu_midnight.yaml"
BACKUP_DIR="$CONFIG_DIR/backups/magguu-dashboard-$(date +%Y%m%d-%H%M%S)"

for required in dashboard/magguu-flux packages/magguu_flux.yaml themes/magguu_midnight.yaml; do
  if [[ ! -e "$SOURCE_DIR/$required" ]]; then
    echo "Fehlende Quelldatei: $SOURCE_DIR/$required" >&2
    exit 1
  fi
done

mkdir -p "$BACKUP_DIR" "$CONFIG_DIR/dashboard" "$CONFIG_DIR/packages" "$CONFIG_DIR/themes"

if [[ -d "$DASHBOARD_TARGET" ]]; then
  cp -a "$DASHBOARD_TARGET" "$BACKUP_DIR/"
fi
if [[ -f "$PACKAGE_TARGET" ]]; then
  cp -a "$PACKAGE_TARGET" "$BACKUP_DIR/"
fi
if [[ -f "$THEME_TARGET" ]]; then
  cp -a "$THEME_TARGET" "$BACKUP_DIR/"
fi

rm -rf "$DASHBOARD_TARGET"
cp -a "$SOURCE_DIR/dashboard/magguu-flux" "$DASHBOARD_TARGET"
cp -a "$SOURCE_DIR/packages/magguu_flux.yaml" "$PACKAGE_TARGET"
cp -a "$SOURCE_DIR/themes/magguu_midnight.yaml" "$THEME_TARGET"

echo "Magguu Dashboard installiert. Backup: $BACKUP_DIR"
echo "Jetzt Home Assistant neu starten und den Browser vollständig neu laden."
