# Verifizierte Home-Assistant-Entitäten

Diese Liste ist die verbindliche Quelle für das Dashboard. Unbekannte Integrationen wie Ring, Nuki, Unraid oder zusätzliche Mediengeräte erst nach Export der echten Entitäts-IDs ergänzen.

## Personen und Smartphone

- `person.magguu`
- `sensor.iphone_von_marco_battery_level`
- `sensor.iphone_von_marco_battery_state`

## Wetter

- `weather.forecast_home`

## Kalender

- `calendar.abfuhr`
- `calendar.arbeiten`
- `calendar.erinnerungen`
- `calendar.privat`
- `calendar.termine`

## Wohnzimmer

- `climate.wohnzimmer_wohnzimmer_thermostat`
- `sensor.wohnzimmer_wohnzimmer_thermostat_temperatur`
- `sensor.wohnzimmer_wohnzimmer_thermostat_rel_luftfeuchte`
- `binary_sensor.wohnzimmer_wohnzimmer_fenster`
- `binary_sensor.wohnzimmer_wohnzimmer_fenstertur_fensterzustand`
- `sensor.wohnzimmer_wohnzimmer_fenstertur`
- `light.wohnzimmer_wohnzimmer`
- `light.wohnzimmer_hue_play_links`
- `light.wohnzimmer_hue_play_rechts`
- `light.wohnzimmer_licht_fenster`
- `light.wohnzimmer_licht_sideboard`
- `light.computerbereich`
- `switch.wohnzimmer_wohnzimmer_fernseher`
- `switch.wohnzimmer_wohnzimmer_computer`
- `cover.wohnzimmer_wohnzimmer_rollade_links`
- `cover.wohnzimmer_wohnzimmer_rollade_mitte`
- `cover.wohnzimmer_wohnzimmer_rollade_rechts`
- `media_player.av_samsung_soundbar_q90r`

## Esszimmer

- `climate.esszimmer_thermostat`
- `sensor.esszimmer_thermostat_temperatur`
- `sensor.esszimmer_thermostat_rel_luftfeuchte`
- `light.esszimmer_esszimmer`
- `light.esszimmer_signe_gradient`
- `switch.esszimmer_esszimmer_licht`

## Küche

- `binary_sensor.kuche_kuche_fenstertur_fensterzustand`
- `sensor.kuche_kuche_fenstertur`
- `switch.kuche_kuche_licht`
- `cover.kuche_kuche_rollade`

## Badezimmer

- `climate.badezimmer_badezimmer_thermostat`
- `sensor.badezimmer_badezimmer_thermostat_temperatur`
- `sensor.badezimmer_badezimmer_thermostat_rel_luftfeuchte`
- `light.badezimmer_badezimmer`
- `light.badezimmer_badezimmer_licht_ch12`
- `light.badezimmer_badezimmer_licht_ch8`
- `light.badezimmer_licht_bad`
- `switch.badezimmer_badezimmer_licht`

## Schlafzimmer

- `climate.schlafzimmer_schlafzimmer_thermostat`
- `sensor.schlafzimmer_schlafzimmer_thermostat_temperatur`
- `sensor.schlafzimmer_schlafzimmer_thermostat_rel_luftfeuchte`
- `binary_sensor.schlafzimmer_schlafzimmer_fenstertur`
- `light.schlafzimmer_schlafzimmer`
- `light.schlafzimmer_bett_links`
- `light.schlafzimmer_bett_rechts`
- `switch.schlafzimmer_schlafzimmer_licht`
- `cover.schlafzimmer_schlafzimmer_rollade_links`
- `cover.schlafzimmer_schlafzimmer_rollade_rechts`

## Kinderzimmer

- `climate.kinderzimmer_kinderzimmer_thermostat`
- `sensor.kinderzimmer_kinderzimmer_thermostat_temperatur`
- `sensor.kinderzimmer_kinderzimmer_thermostat_rel_luftfeuchte`
- `binary_sensor.kinderzimmer_kinderzimmer_fenster`
- `light.kinderzimmer_kinderzimmer`
- `light.kinderzimmer_schrank_licht`
- `switch.kinderzimmer_kinderzimmer_licht`
- `cover.kinderzimmer_kinderzimmer_rollade`

## Flur und Sonstiges

- `switch.flur_flur_licht`
- `light.sonstiges_festavia_string_lights`
- `light.sonstiges_sonstiges`

## OpenCCU und Home Assistant

- `sensor.openccu_servicemeldungen`
- `sensor.openccu_alarmmeldungen`
- `sensor.openccu_systemzustand`
- `sensor.openccu_verbindungslatenz`
- `sensor.homematic_ip_zentrale_duty_cycle_level`
- `sensor.homematic_ip_zentrale_carrier_sense_level`
- `sensor.backup_backup_manager_state`
- `sensor.backup_last_successful_automatic_backup`
- `update.home_assistant_core_update`
- `update.home_assistant_operating_system_update`
- `update.home_assistant_supervisor_update`
- `update.hacs_update`
- `update.mushroom_update`
- `update.openccu_system_update`

## Noch zu ergänzen

- Ring-Kamera und Klingelsensoren
- Nuki-Schloss, Türsensor und Batterie
- Unraid- und Docker-Sensoren
- Plex-/Musik-Entitäten
- AdGuard-Sensoren
