#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${HA_CONFIG_DIR:-/config}"
INSTALLER="$SOURCE_DIR/scripts/install-dashboard.sh"

if [[ ! -f "$INSTALLER" ]]; then
  echo "Fehlende Quelldatei: $INSTALLER" >&2
  exit 1
fi

# shellcheck source=scripts/install-dashboard.sh
. "$INSTALLER"
magguu_install_dashboard "$SOURCE_DIR" "$CONFIG_DIR"

echo "Magguu Dashboard installiert. Backup: $MAGGUU_BACKUP_DIR"
echo "Jetzt Home Assistant neu starten und den Browser vollständig neu laden."
