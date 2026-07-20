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
- Simple Tabs Card
- Stack In Card

## Struktur

- `dashboard/magguu-dashboard/` – aktives YAML-Dashboard
- `dashboard/magguu-dashboard/shared/cards/rooms.yaml` – gemeinsame Raumkarten für Mobile und Tablet
- `dashboard/magguu-dashboard/shared/templates/button_card.yaml` – zentrale UI-Templates
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
cd /config
mkdir -p repos
git clone https://github.com/Derpsen/Magguu-Dashboard.git repos/Magguu-Dashboard
cd repos/Magguu-Dashboard
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
      filename: /config/dashboard/magguu-dashboard/mobile/dashboard.yaml
      title: Zuhause Mobile
      icon: mdi:cellphone
      show_in_sidebar: true

    magguu-tablet:
      mode: yaml
      filename: /config/dashboard/magguu-dashboard/tablet/dashboard.yaml
      title: Zuhause Tablet
      icon: mdi:tablet-dashboard
      show_in_sidebar: true
```

## Update

```bash
bash update.sh
```

Danach Home Assistant neu starten und den Browser vollständig neu laden.

## Aktualisierung

Im geklonten Repository ausführen:

```bash
bash update.sh
```

Das Skript lädt ausschließlich Fast-Forward-Updates und installiert danach Dashboard, Package und Theme mit vorherigem Backup neu. Ein HACS-Dashboard-Repository ist für diese Struktur nicht geeignet, weil HACS-Dashboard-Downloads Frontend-JavaScript unter `www/community` verwalten, nicht YAML-Dashboards und Packages unter mehreren `/config`-Zielen.

Nach der Erstinstallation steht zusätzlich auf der System-Seite die Aktion **Dashboard aktualisieren** bereit. Sie lädt den aktuellen `main`-Stand direkt von GitHub, erstellt ein Backup und aktualisiert alle Dashboard-Dateien. Die Aktion benötigt im Home-Assistant-Container nur `sh`, `curl` und `tar`, nicht `git` oder ein Terminal-Add-on. Nach einem erfolgreichen Update Home Assistant neu starten und die App vollständig neu laden.

Installationen mit den früheren Pfaden `dashboard/magguu-flux` und `packages/magguu_flux.yaml` werden beim nächsten Lauf automatisch migriert. Der Installer sichert die alten Dateien, entfernt doppelte Package-Definitionen und ersetzt die beiden Dashboard-Dateipfade in `configuration.yaml` durch `dashboard/magguu-dashboard`.
