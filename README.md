# Magguu Dashboard

Modulares Home-Assistant-Dashboard für Smartphone, Tablet und Desktop.

## Aktueller Stand

Diese Repository-Version enthält den funktionierenden V5-Dashboardstand als Basis und zusätzlich eine vollständige Entwicklungsstruktur für VS Code und Codex. Die nächste Entwicklungsphase konzentriert sich auf große zusammenhängende Raumkarten, eine modernisierte Home-Seite und spätere Ring-/Nuki-Integration.

## Voraussetzungen

Installierte Frontend-Erweiterungen:

- Mushroom
- Bubble Card
- Button Card
- Layout Card
- Card Mod
- Mini Graph Card
- Auto Entities
- Navbar Card
- Clock Weather Card HUI Icons
- Simple Tabs Card

## Struktur

- `dashboard/magguu-flux/` – aktives YAML-Dashboard
- `packages/` – Template-Sensoren und Hilfslogik
- `themes/` – Magguu Midnight Theme
- `docs/entities.md` – verifizierte Entitäts-IDs
- `docs/design.md` – Designanforderungen
- `AGENTS.md` – verbindliche Regeln für Codex
- `TASKS.md` – Roadmap
- `CODEX_MASTER_PROMPT.md` – erster vollständiger Auftrag

## Installation in Home Assistant

Das Repository nach `/config/repos/Magguu-Dashboard` klonen und anschließend ausführen:

```bash
bash install.sh
```

Die bestehende `configuration.yaml` muss weiterhin auf diese Dateien zeigen:

```yaml
homeassistant:
  packages: !include_dir_named packages

frontend:
  themes: !include_dir_merge_named themes

lovelace:
  dashboards:
    magguu-mobile:
      mode: yaml
      filename: /config/dashboard/magguu-flux/mobile/dashboard.yaml
      title: Zuhause Mobile
      icon: mdi:cellphone
      show_in_sidebar: true

    magguu-tablet:
      mode: yaml
      filename: /config/dashboard/magguu-flux/tablet/dashboard.yaml
      title: Zuhause Tablet
      icon: mdi:tablet-dashboard
      show_in_sidebar: true
```

## Update

```bash
bash update.sh
```

Danach Home Assistant neu starten und den Browser vollständig neu laden.
