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


grep -q 'packages: !include_dir_named packages' "$CONFIG_DIR/configuration.yaml"
grep -q 'themes: !include_dir_merge_named themes' "$CONFIG_DIR/configuration.yaml"
grep -q 'state: "6.4.0-dev"' "$CONFIG_DIR/packages/magguu_dashboard.yaml"
mobile_count="$(grep -c 'magguu-mobile:' "$CONFIG_DIR/configuration.yaml" | tr -d ' ')"
test "$mobile_count" -eq 1
packages_count="$(grep -c 'packages: !include_dir_named packages' "$CONFIG_DIR/configuration.yaml" | tr -d ' ')"
test "$packages_count" -eq 1

# Zweites Install: Merge bleibt idempotent.
HA_CONFIG_DIR="$CONFIG_DIR" sh "$ROOT_DIR/install.sh"
mobile_count="$(grep -c 'magguu-mobile:' "$CONFIG_DIR/configuration.yaml" | tr -d ' ')"
test "$mobile_count" -eq 1
packages_count="$(grep -c 'packages: !include_dir_named packages' "$CONFIG_DIR/configuration.yaml" | tr -d ' ')"
test "$packages_count" -eq 1

# Minimal-Config ohne Lovelace: fehlende Blöcke anhängen, andere Keys nicht anfassen.
MIN_DIR="$TEST_DIR/minimal"
mkdir -p "$MIN_DIR"
printf 'default_config:\n\nname: Magguu\n' > "$MIN_DIR/configuration.yaml"
HA_CONFIG_DIR="$MIN_DIR" sh "$ROOT_DIR/install.sh"
grep -q '^name: Magguu$' "$MIN_DIR/configuration.yaml"
grep -q 'packages: !include_dir_named packages' "$MIN_DIR/configuration.yaml"
grep -q 'themes: !include_dir_merge_named themes' "$MIN_DIR/configuration.yaml"
grep -q 'magguu-mobile:' "$MIN_DIR/configuration.yaml"
grep -q 'magguu-tablet:' "$MIN_DIR/configuration.yaml"

# Vorhandenes Fremd-Dashboard bleibt, Magguu wird unter dashboards ergänzt.
OTHER_DIR="$TEST_DIR/other"
mkdir -p "$OTHER_DIR"
cat > "$OTHER_DIR/configuration.yaml" <<'EOF'
homeassistant:
  name: Haus
frontend:
  extra_module_url:
    - /local/custom.js
lovelace:
  dashboards:
    other-dash:
      mode: yaml
      filename: /config/other.yaml
EOF
HA_CONFIG_DIR="$OTHER_DIR" sh "$ROOT_DIR/install.sh"
grep -q 'name: Haus' "$OTHER_DIR/configuration.yaml"
grep -q 'packages: !include_dir_named packages' "$OTHER_DIR/configuration.yaml"
grep -q 'themes: !include_dir_merge_named themes' "$OTHER_DIR/configuration.yaml"
grep -q 'other-dash:' "$OTHER_DIR/configuration.yaml"
grep -q 'filename: /config/other.yaml' "$OTHER_DIR/configuration.yaml"
grep -q 'magguu-mobile:' "$OTHER_DIR/configuration.yaml"
grep -q 'extra_module_url:' "$OTHER_DIR/configuration.yaml"

# homeassistant als Include: packages nicht erzwingen.
INC_DIR="$TEST_DIR/include"
mkdir -p "$INC_DIR"
cat > "$INC_DIR/configuration.yaml" <<'EOF'
homeassistant: !include homeassistant.yaml
frontend: !include frontend.yaml
EOF
HA_CONFIG_DIR="$INC_DIR" sh "$ROOT_DIR/install.sh"
grep -q 'homeassistant: !include homeassistant.yaml' "$INC_DIR/configuration.yaml"
if grep -q 'packages: !include_dir_named packages' "$INC_DIR/configuration.yaml"; then
  echo "packages wurden in ein homeassistant-!include eingefügt." >&2
  exit 1
fi
grep -q 'magguu-mobile:' "$INC_DIR/configuration.yaml"

echo "Installations- und Update-Prüfung erfolgreich"
