#!/bin/sh

magguu_require_source_files() {
  magguu_source_dir=$1
  for magguu_required in \
    dashboard/magguu-dashboard \
    packages/magguu_dashboard.yaml \
    themes/magguu_midnight.yaml \
    update-ha.sh \
    scripts/install-dashboard.sh
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

  if [ -f "$magguu_config_file" ] && grep -q '/config/dashboard/magguu-flux/' "$magguu_config_file"; then
    cp -a "$magguu_config_file" "$magguu_backup_dir/configuration.yaml"
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

  MAGGUU_BACKUP_DIR=$magguu_backup_dir
  export MAGGUU_BACKUP_DIR
}
