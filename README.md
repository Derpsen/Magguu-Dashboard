# Magguu Dashboard

Modulares Home-Assistant-Dashboard für Smartphone, Tablet und Desktop.

## Aktueller Stand

Diese Repository-Version enthält die moderne V6.4-Basis mit gemeinsamem Midnight-Design für Home, Räume, Klima, Kalender, Sicherheit, Medien, Energie, System und alle sechs Raumdetailseiten plus Flur/Sonstiges. Mobile und Tablet teilen sich die zentralen Inhaltsmodule; gerätespezifisch bleiben nur die responsiven View-Hüllen. Eine priorisierte „Jetzt wichtig“-Logik, Sicherheits- und Wartungsstatus, kontextabhängige Modi, ein bedingter Medienbereich, eine dynamische Abfuhrkarte und gemeinsame informative Raumheader sind integriert. Die Ring-Klingel am Vordereingang und die Kinderzimmer-Kamera sind verdrahtet. Nuki, Unraid, Plex und AdGuard bleiben bewusst ausgeblendet, bis "Unraid & Server" echte Entitäts-IDs liefert; Platzhalter stehen nur in `docs/entities.md`.

## Voraussetzungen

Installierte Frontend-Erweiterungen:

- Mushroom
- Button Card
- Layout Card
- Card Mod
- Mini Graph Card
- Auto Entities
- Navbar Card
- Stack In Card

## Struktur

- `dashboard/magguu-dashboard/` – aktives YAML-Dashboard
- `dashboard/magguu-dashboard/shared/sections/` – gemeinsame Sections (Inhalte aller Seiten) für Mobile und Tablet; nur `max_columns` unterscheidet sich
- `dashboard/magguu-dashboard/shared/cards/` – gemeinsame Inhalte für Home, Räume, Klima, Kalender, Sicherheit, Medien, Energie und System
- `dashboard/magguu-dashboard/shared/rooms/` – gemeinsame responsive Raumdetailseiten
- `dashboard/magguu-dashboard/shared/templates/button_card.yaml` – zentrale UI-Templates
- `packages/` – Template-Sensoren und Hilfslogik
- `VERSION` – einzige Versionsquelle; `packages/magguu_dashboard.yaml` muss denselben Stand haben
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

`install.sh` ergänzt fehlende `packages`-, `themes`- und Magguu-Dashboard-Einträge in `configuration.yaml` (legt vorher ein Backup an und überschreibt vorhandene Keys nicht). Wenn `homeassistant`, `frontend` oder `lovelace` selbst ein `!include` sind, denselben Block manuell setzen:

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

Auf der System-Seite zeigt die Karte **Dashboard-Version** die installierte Version mit Commit (z. B. `6.10.4-dev · 40e8820`) und ob `main` auf GitHub weiter ist („Neuer Stand auf main“). Der Vergleich nutzt die öffentliche GitHub-API (ohne Token, höchstens stündlich); ist sie nicht erreichbar, steht dort „Update-Prüfung unbekannt“. Ein Update gilt als eingespielt, wenn dort `aktuell mit main` steht.

**Optional (nur mit Git-Klon):** Im geklonten Repository `sh update.sh` (Fast-Forward, danach Backup und Neuinstallation). Auf Home Assistant OS ohne Klon ist dieser Weg nicht verfügbar.

Dieses Repository ist **kein HACS-Dashboard**: YAML-Dashboards und Packages liegen unter mehreren `/config`-Zielen; HACS verwaltet Frontend-JavaScript unter `www/community`. Installation und Updates laufen über die Skripte bzw. die System-Aktion oben.

## Docs drift

Docs dürfen dem Repo nicht widersprechen. `bash tools/docs-drift.sh` meldet veraltete Begriffe (Regeln: `.github/docs-drift-rules.txt`), `python3 tools/docs-sync.py` prüft, dass in README, AGENTS, TASKS und `docs/design.md` genannte Pfade existieren (Konfiguration: `.github/docs-sync.txt`). Version, `docs/entities.md` und Custom-Card-Liste prüft weiter `validate.py`, gesperrte Namen `tools/drift-check.sh`. Der wöchentliche Workflow `docs-drift.yml` führt beide Skripte aus; die Repository-Variable `DOCS_DRIFT_MODE` wählt `issue` (Standard: ein deduplizierter „Docs-Drift“-Issue, wird bei sauberem Lauf geschlossen), `warn` (Annotationen bei jedem Push/PR) oder `fail`. Beide Skripte laufen auch im Pre-push-Hook.

## Git pre-push hook

Enable the in-repo pre-push checks once per checkout: `git config core.hooksPath .githooks`
