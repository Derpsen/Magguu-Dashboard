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

# Literal state of the template sensor with the given unique_id in a package file.
stamped_state() {
  awk -v id="$2" '
    $0 ~ ("unique_id:[ ]+" id "[ ]*$") { hit=1 }
    hit && /state:/ { sub(/^.*state: "/, ""); sub(/".*$/, ""); print; exit }
  ' "$1"
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
PACKAGE_FILE="$CONFIG_DIR/packages/magguu_dashboard.yaml"
VERSION_TEXT="$(tr -d '\r\n' < "$ROOT_DIR/VERSION")"
test "$(stamped_state "$PACKAGE_FILE" magguu_dashboard_version)" = "$VERSION_TEXT"
# Clone install (install.sh): commit comes from git, or "unbekannt" without a clone.
if [ -e "$ROOT_DIR/.git" ] && command -v git >/dev/null 2>&1 && git -C "$ROOT_DIR" rev-parse HEAD >/dev/null 2>&1; then
  test "$(stamped_state "$PACKAGE_FILE" magguu_dashboard_commit)" = "$(git -C "$ROOT_DIR" rev-parse HEAD)"
else
  test "$(stamped_state "$PACKAGE_FILE" magguu_dashboard_commit)" = "unbekannt"
fi
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
  -e "s#^CURL_PROTO='=https'\$#CURL_PROTO='=file'#" \
  "$ROOT_DIR/update-ha.sh" > "$UPDATER"
grep -q "^CONFIG_DIR=$CONFIG_DIR\$" "$UPDATER"
grep -q "^ARCHIVE_URL=file://" "$UPDATER"
grep -q "^CURL_PROTO='=file'\$" "$UPDATER"
# The shipped updater only allows https downloads (a file:// archive must fail).
sed -e "s#^CONFIG_DIR=/config\$#CONFIG_DIR=$CONFIG_DIR#" \
  -e "s#^ARCHIVE_URL=https://github.com/Derpsen/Magguu-Dashboard/archive/refs/heads/main.tar.gz\$#ARCHIVE_URL=file://$TEST_DIR/main.tar.gz#" \
  "$ROOT_DIR/update-ha.sh" > "$TEST_DIR/update-ha-https.sh"
if sh "$TEST_DIR/update-ha-https.sh" >/dev/null 2>&1; then
  echo "Updater hat ein file://-Archiv trotz --proto =https akzeptiert." >&2
  exit 1
fi
test -f "$CONFIG_DIR/dashboard/magguu-dashboard/outdated.marker"
sh "$UPDATER"
test ! -e "$CONFIG_DIR/dashboard/magguu-dashboard/outdated.marker"
# Archive without GitHub pax header: commit stays "unbekannt"; env cannot inject one.
test "$(stamped_state "$PACKAGE_FILE" magguu_dashboard_commit)" = "unbekannt"
MAGGUU_COMMIT_SHA=ffffffffffffffffffffffffffffffffffffffff sh "$UPDATER" >/dev/null
test "$(stamped_state "$PACKAGE_FILE" magguu_dashboard_commit)" = "unbekannt"
test "$(stamped_state "$PACKAGE_FILE" magguu_dashboard_version)" = "$VERSION_TEXT"

# Archive in GitHub format (git archive writes the commit into the pax header).
if command -v git >/dev/null 2>&1; then
  GIT_SRC="$TEST_DIR/gitsrc"
  mkdir -p "$GIT_SRC"
  (cd "$ROOT_DIR" && tar --exclude=.git -cf - .) | (cd "$GIT_SRC" && tar -xf -)
  (
    cd "$GIT_SRC"
    git init -q
    git add -A
    git -c user.name=test -c user.email=test@example.invalid -c commit.gpgsign=false commit -q -m test
    git archive --format=tar.gz --prefix=Magguu-Dashboard-main/ -o "$TEST_DIR/main.tar.gz" HEAD
  )
  EXPECTED_SHA="$(git -C "$GIT_SRC" rev-parse HEAD)"
  sleep 1
  sh "$UPDATER" >/dev/null
  test "$(stamped_state "$PACKAGE_FILE" magguu_dashboard_commit)" = "$EXPECTED_SHA"
  test "$(stamped_state "$PACKAGE_FILE" magguu_dashboard_version)" = "$VERSION_TEXT"
  grep -q 'unique_id: magguu_dashboard_update_hinweis' "$PACKAGE_FILE"
fi

# Commit detection accepts only a full lowercase 40-char hex SHA.
(
  # shellcheck source=scripts/install-dashboard.sh
  . "$ROOT_DIR/scripts/install-dashboard.sh"
  good=0123456789abcdef0123456789abcdef01234567
  NOGIT="$TEST_DIR/nogit"
  mkdir -p "$NOGIT"
  MAGGUU_COMMIT_SHA=$good
  test "$(magguu_detect_commit "$NOGIT")" = "$good"
  for bad in "" 0123456789ABCDEF0123456789ABCDEF01234567 0123456789abcdef '0123456789abcdef0123456789abcdef0123456"; x' \
    0123456789abcdef0123456789abcdef012345678; do
    MAGGUU_COMMIT_SHA=$bad
    test "$(magguu_detect_commit "$NOGIT")" = "unbekannt"
  done
)

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
grep -q "state: \"$VERSION_TEXT\"" "$CONFIG_DIR/packages/magguu_dashboard.yaml"
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
