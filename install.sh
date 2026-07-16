#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
DASHBOARD_TARGET="$CONFIG_DIR/dashboard/magguu-dashboard"
PACKAGE_TARGET="$CONFIG_DIR/packages/magguu_dashboard.yaml"
THEME_TARGET="$CONFIG_DIR/themes/magguu_midnight.yaml"
UPDATER_TARGET="$CONFIG_DIR/magguu-dashboard-update.sh"
LEGACY_DASHBOARD_TARGET="$CONFIG_DIR/dashboard/magguu-flux"
LEGACY_PACKAGE_TARGET="$CONFIG_DIR/packages/magguu_flux.yaml"
CONFIG_FILE="$CONFIG_DIR/configuration.yaml"
BACKUP_DIR="$CONFIG_DIR/backups/magguu-dashboard-$(date +%Y%m%d-%H%M%S)"

for required in dashboard/magguu-dashboard packages/magguu_dashboard.yaml themes/magguu_midnight.yaml update-ha.sh; do
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
if [[ -d "$LEGACY_DASHBOARD_TARGET" ]]; then
  cp -a "$LEGACY_DASHBOARD_TARGET" "$BACKUP_DIR/"
fi
if [[ -f "$LEGACY_PACKAGE_TARGET" ]]; then
  cp -a "$LEGACY_PACKAGE_TARGET" "$BACKUP_DIR/"
fi

if [[ -f "$CONFIG_FILE" ]] && grep -q '/config/dashboard/magguu-flux/' "$CONFIG_FILE"; then
  cp -a "$CONFIG_FILE" "$BACKUP_DIR/configuration.yaml"
  sed 's#/config/dashboard/magguu-flux/#/config/dashboard/magguu-dashboard/#g' "$CONFIG_FILE" > "$CONFIG_FILE.magguu-new"
  mv "$CONFIG_FILE.magguu-new" "$CONFIG_FILE"
fi

rm -rf "$DASHBOARD_TARGET"
rm -rf "$LEGACY_DASHBOARD_TARGET"
rm -f "$LEGACY_PACKAGE_TARGET"
cp -a "$SOURCE_DIR/dashboard/magguu-dashboard" "$DASHBOARD_TARGET"
cp -a "$SOURCE_DIR/packages/magguu_dashboard.yaml" "$PACKAGE_TARGET"
cp -a "$SOURCE_DIR/themes/magguu_midnight.yaml" "$THEME_TARGET"
cp -a "$SOURCE_DIR/update-ha.sh" "$UPDATER_TARGET"
chmod 755 "$UPDATER_TARGET"

echo "Magguu Dashboard installiert. Backup: $BACKUP_DIR"
echo "Jetzt Home Assistant neu starten und den Browser vollständig neu laden."
