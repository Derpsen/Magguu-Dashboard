#!/bin/sh

magguu_require_source_files() {
  magguu_source_dir=$1
  for magguu_required in \
    dashboard/magguu-dashboard \
    packages/magguu_dashboard.yaml \
    themes/magguu_midnight.yaml \
    update-ha.sh \
    scripts/install-dashboard.sh \
    VERSION
  do
    if [ ! -e "$magguu_source_dir/$magguu_required" ]; then
      echo "Fehlende Quelldatei: $magguu_source_dir/$magguu_required" >&2
      return 1
    fi
  done
}

magguu_backup_if_exists() {
  magguu_backup_source=$1
  magguu_backup_dir=$2
  if [ -e "$magguu_backup_source" ]; then
    cp -a "$magguu_backup_source" "$magguu_backup_dir/"
  fi
}

magguu_config_has_key() {
  magguu_file=$1
  magguu_key=$2
  grep -Eq "^[[:space:]]*${magguu_key}:" "$magguu_file"
}

magguu_parent_is_include() {
  magguu_file=$1
  magguu_key=$2
  grep -Eq "^${magguu_key}:[[:space:]]+!include" "$magguu_file"
}

magguu_mapping_key_line() {
  magguu_file=$1
  magguu_key=$2
  grep -Eq "^${magguu_key}:[[:space:]]*(#|$)" "$magguu_file"
}

magguu_insert_file_after() {
  magguu_file=$1
  magguu_pattern=$2
  magguu_insert_file=$3
  magguu_tmp="$magguu_file.magguu-new"
  awk -v pat="$magguu_pattern" -v insfile="$magguu_insert_file" '
    BEGIN { done=0 }
    {
      print $0
      if (!done && $0 ~ pat) {
        while ((getline line < insfile) > 0) print line
        close(insfile)
        done=1
      }
    }
    END { if (!done) exit 2 }
  ' "$magguu_file" > "$magguu_tmp" || {
    rm -f "$magguu_tmp"
    return 1
  }
  mv "$magguu_tmp" "$magguu_file"
}

magguu_append_block() {
  magguu_file=$1
  magguu_block=$2
  printf '\n%s\n' "$magguu_block" >> "$magguu_file"
}

magguu_write_temp_line() {
  magguu_path=$1
  magguu_line=$2
  printf '%s\n' "$magguu_line" > "$magguu_path"
}

magguu_dashboard_block() {
  magguu_indent=$1
  magguu_pad=$(awk -v n="$magguu_indent" 'BEGIN { while (n-- > 0) printf " " }')
  magguu_child=$(awk -v n="$((magguu_indent + 2))" 'BEGIN { while (n-- > 0) printf " " }')
  printf '%s\n' \
    "${magguu_pad}magguu-mobile:" \
    "${magguu_child}mode: yaml" \
    "${magguu_child}filename: /config/dashboard/magguu-dashboard/mobile/dashboard.yaml" \
    "${magguu_child}title: Zuhause Mobile" \
    "${magguu_child}icon: mdi:cellphone" \
    "${magguu_child}show_in_sidebar: true" \
    "${magguu_pad}magguu-tablet:" \
    "${magguu_child}mode: yaml" \
    "${magguu_child}filename: /config/dashboard/magguu-dashboard/tablet/dashboard.yaml" \
    "${magguu_child}title: Zuhause Tablet" \
    "${magguu_child}icon: mdi:tablet-dashboard" \
    "${magguu_child}show_in_sidebar: true"
}

magguu_configuration_needs_merge() {
  magguu_file=$1
  [ -f "$magguu_file" ] || return 1
  magguu_config_has_key "$magguu_file" "packages" || return 0
  magguu_config_has_key "$magguu_file" "themes" || return 0
  magguu_config_has_key "$magguu_file" "magguu-mobile" || return 0
  return 1
}

magguu_merge_ha_configuration() {
  magguu_file=$1
  magguu_tmpdir=$2
  [ -f "$magguu_file" ] || return 0
  magguu_linefile="$magguu_tmpdir/magguu-insert.txt"

  if ! magguu_config_has_key "$magguu_file" "packages"; then
    if magguu_parent_is_include "$magguu_file" "homeassistant"; then
      echo "Hinweis: homeassistant ist ein !include – packages nicht automatisch ergänzt." >&2
    elif magguu_mapping_key_line "$magguu_file" "homeassistant"; then
      magguu_write_temp_line "$magguu_linefile" "  packages: !include_dir_named packages"
      magguu_insert_file_after "$magguu_file" '^homeassistant:[[:space:]]*(#|$)' "$magguu_linefile"
    elif magguu_config_has_key "$magguu_file" "homeassistant"; then
      echo "Hinweis: homeassistant-Block nicht eindeutig – packages nicht automatisch ergänzt." >&2
    else
      magguu_append_block "$magguu_file" "homeassistant:
  packages: !include_dir_named packages"
    fi
  fi

  if ! magguu_config_has_key "$magguu_file" "themes"; then
    if magguu_parent_is_include "$magguu_file" "frontend"; then
      echo "Hinweis: frontend ist ein !include – themes nicht automatisch ergänzt." >&2
    elif magguu_mapping_key_line "$magguu_file" "frontend"; then
      magguu_write_temp_line "$magguu_linefile" "  themes: !include_dir_merge_named themes"
      magguu_insert_file_after "$magguu_file" '^frontend:[[:space:]]*(#|$)' "$magguu_linefile"
    elif magguu_config_has_key "$magguu_file" "frontend"; then
      echo "Hinweis: frontend-Block nicht eindeutig – themes nicht automatisch ergänzt." >&2
    else
      magguu_append_block "$magguu_file" "frontend:
  themes: !include_dir_merge_named themes"
    fi
  fi

  if ! magguu_config_has_key "$magguu_file" "magguu-mobile"; then
    if magguu_parent_is_include "$magguu_file" "lovelace"; then
      echo "Hinweis: lovelace ist ein !include – Dashboards nicht automatisch ergänzt." >&2
    elif magguu_config_has_key "$magguu_file" "dashboards"; then
      magguu_dash_line=$(grep -E '^[[:space:]]*dashboards:[[:space:]]*(#|$)' "$magguu_file" | head -n 1)
      magguu_indent=$(printf '%s\n' "$magguu_dash_line" | awk '{ match($0, /^[ ]*/); print RLENGTH + 2 }')
      magguu_dashboard_block "$magguu_indent" > "$magguu_linefile"
      magguu_insert_file_after "$magguu_file" '^[[:space:]]*dashboards:[[:space:]]*(#|$)' "$magguu_linefile"
    elif magguu_mapping_key_line "$magguu_file" "lovelace"; then
      printf '%s\n' "  dashboards:" > "$magguu_linefile"
      magguu_dashboard_block 4 >> "$magguu_linefile"
      magguu_insert_file_after "$magguu_file" '^lovelace:[[:space:]]*(#|$)' "$magguu_linefile"
    elif magguu_config_has_key "$magguu_file" "lovelace"; then
      echo "Hinweis: lovelace-Block nicht eindeutig – Dashboards nicht automatisch ergänzt." >&2
    else
      magguu_append_block "$magguu_file" "lovelace:
  dashboards:
    magguu-mobile:
      mode: yaml
      filename: /config/dashboard/magguu-dashboard/mobile/dashboard.yaml
      title: Zuhause Mobile
      icon: mdi:cellphone
      show_in_sidebar: true

    magguu-tablet:
      mode: yaml
      filename: /config/dashboard/magguu-dashboard/tablet/dashboard.yaml
      title: Zuhause Tablet
      icon: mdi:tablet-dashboard
      show_in_sidebar: true"
    fi
  fi
}

magguu_stamp_package_version() {
  magguu_version_file=$1
  magguu_package=$2
  magguu_version=$(tr -d '\r\n' < "$magguu_version_file")
  magguu_tmp="$magguu_package.magguu-new"
  awk -v ver="$magguu_version" '
    BEGIN { hit=0 }
    /unique_id: magguu_dashboard_version/ { hit=1 }
    {
      if (hit && $0 ~ /state:/) {
        sub(/state: ".*"/, "state: \"" ver "\"")
        hit=0
      }
      print
    }
  ' "$magguu_package" > "$magguu_tmp"
  mv "$magguu_tmp" "$magguu_package"
}

magguu_install_dashboard() {
  magguu_source_dir=$1
  magguu_config_dir=$2
  magguu_dashboard_target="$magguu_config_dir/dashboard/magguu-dashboard"
  magguu_package_target="$magguu_config_dir/packages/magguu_dashboard.yaml"
  magguu_theme_target="$magguu_config_dir/themes/magguu_midnight.yaml"
  magguu_updater_target="$magguu_config_dir/magguu-dashboard-update.sh"
  magguu_legacy_dashboard_target="$magguu_config_dir/dashboard/magguu-flux"
  magguu_legacy_package_target="$magguu_config_dir/packages/magguu_flux.yaml"
  magguu_config_file="$magguu_config_dir/configuration.yaml"
  magguu_backup_dir="$magguu_config_dir/backups/magguu-dashboard-$(date +%Y%m%d-%H%M%S)"

  magguu_require_source_files "$magguu_source_dir"
  mkdir -p \
    "$magguu_backup_dir" \
    "$magguu_config_dir/dashboard" \
    "$magguu_config_dir/packages" \
    "$magguu_config_dir/themes"

  magguu_backup_if_exists "$magguu_dashboard_target" "$magguu_backup_dir"
  magguu_backup_if_exists "$magguu_package_target" "$magguu_backup_dir"
  magguu_backup_if_exists "$magguu_theme_target" "$magguu_backup_dir"
  magguu_backup_if_exists "$magguu_legacy_dashboard_target" "$magguu_backup_dir"
  magguu_backup_if_exists "$magguu_legacy_package_target" "$magguu_backup_dir"

  magguu_config_backed_up=0
  if [ -f "$magguu_config_file" ] && grep -q '/config/dashboard/magguu-flux/' "$magguu_config_file"; then
    magguu_backup_if_exists "$magguu_config_file" "$magguu_backup_dir"
    magguu_config_backed_up=1
    sed 's#/config/dashboard/magguu-flux/#/config/dashboard/magguu-dashboard/#g' \
      "$magguu_config_file" > "$magguu_config_file.magguu-new"
    mv "$magguu_config_file.magguu-new" "$magguu_config_file"
  fi

  rm -rf "$magguu_dashboard_target" "$magguu_legacy_dashboard_target"
  rm -f "$magguu_legacy_package_target"
  cp -a "$magguu_source_dir/dashboard/magguu-dashboard" "$magguu_dashboard_target"
  cp -a "$magguu_source_dir/packages/magguu_dashboard.yaml" "$magguu_package_target"
  cp -a "$magguu_source_dir/themes/magguu_midnight.yaml" "$magguu_theme_target"
  cp -a "$magguu_source_dir/update-ha.sh" "$magguu_updater_target"
  chmod 755 "$magguu_updater_target"
  magguu_stamp_package_version "$magguu_source_dir/VERSION" "$magguu_package_target"

  if [ -f "$magguu_config_file" ] && magguu_configuration_needs_merge "$magguu_config_file"; then
    if [ "$magguu_config_backed_up" -eq 0 ]; then
      magguu_backup_if_exists "$magguu_config_file" "$magguu_backup_dir"
    fi
    magguu_merge_ha_configuration "$magguu_config_file" "$magguu_backup_dir"
  fi

  MAGGUU_BACKUP_DIR=$magguu_backup_dir
  export MAGGUU_BACKUP_DIR
}
