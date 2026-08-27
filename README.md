# Magguu Dashboard

Modulares Home-Assistant-Dashboard für Smartphone, Tablet und Desktop.

## Aktueller Stand

Diese Repository-Version enthält die moderne V6.4-Basis mit gemeinsamem Midnight-Design für Home, Räume, Klima, Kalender, Sicherheit, Medien, Energie, System und alle sechs Raumdetailseiten. Mobile und Tablet teilen sich die zentralen Inhaltsmodule; gerätespezifisch bleiben nur die responsiven View-Hüllen. Eine priorisierte „Jetzt wichtig“-Logik, Sicherheits- und Wartungsstatus, kontextabhängige Modi, ein bedingter Medienbereich, eine dynamische Abfuhrkarte und gemeinsame informative Raumheader sind integriert. Die Ring-Klingel am Vordereingang und die Kinderzimmer-Kamera sind verdrahtet. Nuki, Unraid, Plex und AdGuard bleiben bewusst ausgeblendet, bis Homelab echte Entitäts-IDs liefert; Platzhalter stehen nur in `docs/entities.md`.

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
- Stack In Card

## Struktur

- `dashboard/magguu-dashboard/` – aktives YAML-Dashboard
- `dashboard/magguu-dashboard/shared/cards/rooms.yaml` – gemeinsame Raumkarten für Mobile und Tablet
- `dashboard/magguu-dashboard/shared/cards/` – gemeinsame Inhalte für Home, Räume, Klima, Kalender, Sicherheit, Medien, Energie und System
- `dashboard/magguu-dashboard/shared/rooms/` – gemeinsame responsive Raumdetailseiten
- `dashboard/magguu-dashboard/shared/templates/button_card.yaml` – zentrale UI-Templates
- `packages/` – Template-Sensoren und Hilfslogik
- `themes/` – Magguu Midnight Theme
- `docs/entities.md` – verifizierte Entitäts-IDs
- `docs/design.md` – Designanforderungen
- `AGENTS.md` – verbindliche Regeln für Assistenten (Buddy-Hub)
- `TASKS.md` – Roadmap

## Installation in Home Assistant

Das Repository nach `/config/repos/Magguu-Dashboard` klonen und anschließend ausführen:

```bash
cd /config
mkdir -p repos
git clone https://github.com/Derpsen/Magguu-Dashboard.git repos/Magguu-Dashboard
cd repos/Magguu-Dashboard
sh install.sh
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

## Aktualisieren

**Primär:** Auf der System-Seite **Dashboard aktualisieren**. Das lädt `main` von GitHub als Tarball (`update-ha.sh` mit `sh`/`curl`/`tar`), legt ein Backup an und ist der HA-OS-Weg – kein Git-Klon und kein Terminal-Add-on nötig.

Danach Home Assistant neu starten und die App vollständig neu laden.

**Optional (nur mit Git-Klon):** Im geklonten Repository `sh update.sh` (Fast-Forward, danach Backup und Neuinstallation). Auf Home Assistant OS ohne Klon ist dieser Weg nicht verfügbar.

Dieses Repository ist **kein HACS-Dashboard**: YAML-Dashboards und Packages liegen unter mehreren `/config`-Zielen; HACS verwaltet Frontend-JavaScript unter `www/community`. Installation und Updates laufen über die Skripte bzw. die System-Aktion oben.
