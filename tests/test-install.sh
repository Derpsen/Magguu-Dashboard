#!/bin/sh
set -eu

ROOT_DIR="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
TEST_DIR="$(mktemp -d)"
CONFIG_DIR="$TEST_DIR/config"

cleanup() {
  rm -rf "$TEST_DIR"
}
trap cleanup EXIT INT TERM

assert_file() {
  if [ ! -f "$1" ]; then
    echo "Erwartete Datei fehlt: $1" >&2
    exit 1
  fi
}

mkdir -p "$CONFIG_DIR/dashboard/magguu-flux" "$CONFIG_DIR/packages"
printf 'legacy\n' > "$CONFIG_DIR/dashboard/magguu-flux/legacy.yaml"
printf 'legacy\n' > "$CONFIG_DIR/packages/magguu_flux.yaml"
cat > "$CONFIG_DIR/configuration.yaml" <<'EOF'
lovelace:
  dashboards:
    magguu-mobile:
      filename: /config/dashboard/magguu-flux/mobile/dashboard.yaml
    magguu-tablet:
      filename: /config/dashboard/magguu-flux/tablet/dashboard.yaml
EOF

HA_CONFIG_DIR="$CONFIG_DIR" sh "$ROOT_DIR/install.sh"
assert_file "$CONFIG_DIR/dashboard/magguu-dashboard/mobile/dashboard.yaml"
assert_file "$CONFIG_DIR/dashboard/magguu-dashboard/tablet/dashboard.yaml"
assert_file "$CONFIG_DIR/packages/magguu_dashboard.yaml"
assert_file "$CONFIG_DIR/themes/magguu_midnight.yaml"
assert_file "$CONFIG_DIR/magguu-dashboard-update.sh"
test -x "$CONFIG_DIR/magguu-dashboard-update.sh"
test ! -e "$CONFIG_DIR/dashboard/magguu-flux"
test ! -e "$CONFIG_DIR/packages/magguu_flux.yaml"
grep -q '/config/dashboard/magguu-dashboard/mobile/dashboard.yaml' "$CONFIG_DIR/configuration.yaml"
grep -q '/config/dashboard/magguu-dashboard/tablet/dashboard.yaml' "$CONFIG_DIR/configuration.yaml"
if grep -q 'magguu-flux\|magguu_flux' "$CONFIG_DIR/configuration.yaml"; then
  echo "Legacy-Pfade wurden nicht vollständig migriert." >&2
  exit 1
fi

printf 'outdated\n' > "$CONFIG_DIR/dashboard/magguu-dashboard/outdated.marker"
HA_CONFIG_DIR="$CONFIG_DIR" \
  MAGGUU_DASHBOARD_SOURCE_DIR="$ROOT_DIR" \
  sh "$ROOT_DIR/update-ha.sh"
test ! -e "$CONFIG_DIR/dashboard/magguu-dashboard/outdated.marker"

backup_count="$(find "$CONFIG_DIR/backups" -type f -name outdated.marker | wc -l | tr -d ' ')"
test "$backup_count" -eq 1

echo "Installations- und Update-Prüfung erfolgreich"
