#!/bin/sh
set -eu

ROOT_DIR="$(CDPATH='' cd -- "$(dirname "$0")/.." && pwd)"
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
# update-ha.sh reads no args/env (shell_command is callable by any HA user):
# run a copy with the two fixed lines pointed at the test dir and a local archive.
ARCHIVE_SRC="$TEST_DIR/archive/Magguu-Dashboard-main"
mkdir -p "$ARCHIVE_SRC"
(cd "$ROOT_DIR" && tar --exclude=.git -cf - .) | (cd "$ARCHIVE_SRC" && tar -xf -)
tar -czf "$TEST_DIR/main.tar.gz" -C "$TEST_DIR/archive" Magguu-Dashboard-main
UPDATER="$TEST_DIR/update-ha.sh"
sed -e "s#^CONFIG_DIR=/config\$#CONFIG_DIR=$CONFIG_DIR#" \
  -e "s#^ARCHIVE_URL=https://github.com/Derpsen/Magguu-Dashboard/archive/refs/heads/main.tar.gz\$#ARCHIVE_URL=file://$TEST_DIR/main.tar.gz#" \
  "$ROOT_DIR/update-ha.sh" > "$UPDATER"
grep -q "^CONFIG_DIR=$CONFIG_DIR\$" "$UPDATER"
grep -q "^ARCHIVE_URL=file://" "$UPDATER"
sh "$UPDATER"
test ! -e "$CONFIG_DIR/dashboard/magguu-dashboard/outdated.marker"

backup_count="$(find "$CONFIG_DIR/backups" -type f -name outdated.marker | wc -l | tr -d ' ')"
test "$backup_count" -eq 1

LOCK_DIR="$CONFIG_DIR/.magguu-dashboard-update.lockdir"
LOCK_FILE="$CONFIG_DIR/.magguu-dashboard-update.lock"
test ! -e "$LOCK_DIR"
MKDIR_UPDATER="$TEST_DIR/update-ha-mkdir.sh"
sed -e 's#^LOCK_MODE=auto$#LOCK_MODE=mkdir#' "$UPDATER" > "$MKDIR_UPDATER"
grep -q '^LOCK_MODE=mkdir$' "$MKDIR_UPDATER"

count_backups() {
  find "$CONFIG_DIR/backups" -mindepth 1 -maxdepth 1 -type d -name 'magguu-dashboard-*' | wc -l | tr -d ' '
}

assert_skipped() {
  # $1 = output of the skipped run, $2 = backup count before
  printf '%s\n' "$1" | grep -q 'läuft bereits'
  test -f "$CONFIG_DIR/dashboard/magguu-dashboard/outdated.marker"
  test "$(count_backups)" -eq "$2"
  if find "$CONFIG_DIR" -maxdepth 1 -name '.magguu-dashboard-update.??????' | grep -q .; then
    echo "Übersprungener Lauf hat ein Arbeitsverzeichnis angelegt." >&2
    exit 1
  fi
}

# Parallellauf (mkdir-Lock, frisch): Exit 0, keine Wirkung, fremde Sperre bleibt.
sleep 1
printf 'outdated\n' > "$CONFIG_DIR/dashboard/magguu-dashboard/outdated.marker"
before="$(count_backups)"
mkdir "$LOCK_DIR"
out="$(sh "$MKDIR_UPDATER")"
assert_skipped "$out" "$before"
test -d "$LOCK_DIR"

# Parallellauf (flock, Standardmodus): gehaltene Sperre -> Exit 0, keine Wirkung.
if command -v flock >/dev/null 2>&1; then
  rmdir "$LOCK_DIR"
  (
    exec 9>"$LOCK_FILE"
    flock 9
    : > "$TEST_DIR/flock-held"
    while [ ! -e "$TEST_DIR/flock-release" ]; do sleep 0.1; done
  ) &
  holder=$!
  while [ ! -e "$TEST_DIR/flock-held" ]; do sleep 0.1; done
  out="$(sh "$UPDATER")"
  : > "$TEST_DIR/flock-release"
  wait "$holder"
  assert_skipped "$out" "$before"
  mkdir "$LOCK_DIR"
fi

# Veraltete Sperre (> 10 min) wird übernommen und am Ende freigegeben.
touch -d "@$(( $(date +%s) - 900 ))" "$LOCK_DIR"
# Rotation: alte Magguu-Backups + fremde Dateien im Backup-Verzeichnis.
for day in 01 02 03 04 05 06 07; do
  mkdir -p "$CONFIG_DIR/backups/magguu-dashboard-202001${day}-000000"
done
mkdir -p "$CONFIG_DIR/backups/other-backup" "$CONFIG_DIR/backups/magguu-dashboard-20200101-000000-keep"
printf 'x\n' > "$CONFIG_DIR/backups/notes.txt"
printf 'x\n' > "$CONFIG_DIR/backups/magguu-dashboard-20190101-000000"
printf 'x\n' > "$CONFIG_DIR/backups/magguu-dashboard-20190101-000000.tar"
ln -s other-backup "$CONFIG_DIR/backups/magguu-dashboard-20180101-000000"
out="$(sh "$MKDIR_UPDATER")"
printf '%s\n' "$out" | grep -q 'Veraltete Update-Sperre'
printf '%s\n' "$out" | grep -q 'Magguu Dashboard aktualisiert'
test ! -e "$CONFIG_DIR/dashboard/magguu-dashboard/outdated.marker"
test ! -e "$LOCK_DIR"

# Genau 5 Magguu-Backups (neueste), Rest im Backup-Verzeichnis unberührt.
magguu_backups="$(find "$CONFIG_DIR/backups" -mindepth 1 -maxdepth 1 -type d \
  -name 'magguu-dashboard-[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9]' | wc -l | tr -d ' ')"
test "$magguu_backups" -eq 5
test ! -e "$CONFIG_DIR/backups/magguu-dashboard-20200101-000000"
test ! -e "$CONFIG_DIR/backups/magguu-dashboard-20200103-000000"
newest="$(find "$CONFIG_DIR/backups" -mindepth 1 -maxdepth 1 -type d -name 'magguu-dashboard-20[3-9]*' -o -type d -name 'magguu-dashboard-202[1-9]*' | wc -l | tr -d ' ')"
test "$newest" -ge 2
test -d "$CONFIG_DIR/backups/other-backup"
test -d "$CONFIG_DIR/backups/magguu-dashboard-20200101-000000-keep"
test -f "$CONFIG_DIR/backups/notes.txt"
test -f "$CONFIG_DIR/backups/magguu-dashboard-20190101-000000"
test -f "$CONFIG_DIR/backups/magguu-dashboard-20190101-000000.tar"
test -L "$CONFIG_DIR/backups/magguu-dashboard-20180101-000000"


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
