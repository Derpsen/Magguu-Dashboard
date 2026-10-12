# Magguu Dashboard – Arbeitsregeln für Assistenten

## Ziel

Dieses Repository enthält ein vollständig YAML-basiertes Home-Assistant-Dashboard für Smartphone, Tablet und Desktop. Es soll sich wie eine hochwertige Smart-Home-App anfühlen und nicht wie eine lose Sammlung von Lovelace-Karten.

## Grok Bot / Buddy

Marco nutzt Grok Bot „Buddy“ als einzige Front Door. Helfer melden Ergebnisse an Buddy zurück.

- Interaktive/Ad-hoc-Sessions: kein Commit, Push oder Git-Tag ohne ausdrückliche Freigabe für genau diesen Schritt.
- Helfer unter Buddy-Hub-Standing-Order: klare In-Scope-Fixes dürfen ohne Nachfrage pro Änderung committen, pushen und nach `main` mergen; niemals force-push; niemals unzusammenhängendes dirty WIP mitveröffentlichen; Tags/Releases brauchen eine ausdrückliche Release-Freigabe.

## Unverhandelbare Regeln

- Vor Änderungen das gesamte betroffene Modul lesen.
- Bestehende Entitäts-IDs niemals erraten oder stillschweigend ändern.
- Neue Entitäten nur aus `docs/entities.md` verwenden oder als klar markiertes TODO dokumentieren.
- Home-Assistant-Tags wie `!include`, `!include_dir_merge_list` und `!include_dir_merge_named` erhalten.
- Keine unnötigen HACS-Abhängigkeiten hinzufügen.
- Gemeinsame Logik über Templates wiederverwenden; kein Copy-and-paste zwischen Mobile und Tablet.
- Mobile und Tablet nach jeder Layoutänderung gemeinsam prüfen.
- Keine funktionierende Seite entfernen, ohne Ersatz und Changelog-Eintrag.
- Keine Zugangsdaten, Tokens, Hostnamen oder privaten URLs committen.
- Änderungen klein, nachvollziehbar und rückrollbar halten.
- Kein ElvUI-/WoW-Addon-Ballast in dieses Home-Assistant-Repo einbringen.

## Designsystem

- Dunkles Midnight-Design mit ruhigen Flächen.
- Große, zusammenhängende Raumkarten statt vieler kleiner Standardkarten.
- Aktive Elemente erhalten Farbe und einen dezenten Glow.
- Licht: warmes Gold.
- Klima und Wasser: Blau/Türkis.
- Erfolgreicher/geschlossener Zustand: Grün nur sparsam.
- Warnung: Orange.
- Fehler: Rot.
- Inaktive Zustände neutral und kontrastarm.
- Abstände, Radien und Typografie über zentrale Templates bzw. Theme-Variablen steuern.
- Animationen dezent und performant; keine Daueranimationen ohne Informationswert.

## Seiten

- Home
- Räume
- Kalender
- Klima
- Medien
- Sicherheit
- Energie
- System

## Raumkarten

Jede Raumkarte soll möglichst in einer einzigen zusammenhängenden Karte enthalten:

- Raumname
- großes Raumsymbol
- Temperatur und Luftfeuchtigkeit
- Fenster-/Türstatus
- Anzahl aktiver Lichter
- wichtigste direkte Aktionen
- Navigation zur Raumdetailseite
- aktive Zustände visuell hervorgehoben

## Qualitätssicherung

Nach jeder Änderung:

1. YAML-Dateien syntaktisch prüfen.
2. Include-Pfade prüfen.
3. Entitäts-IDs gegen `docs/entities.md` prüfen.
4. Mobile und Tablet auf doppelte oder abweichende Logik prüfen.
5. `CHANGELOG.md` aktualisieren.
6. Einen kurzen Commit-Vorschlag nennen (Buddy/Helfer: bei klaren In-Scope-Fixes laut Standing Order selbst committen/pushen/mergen).

## Arbeitsweise

- Erst analysieren, dann einen konkreten Plan nennen, danach umsetzen.
- Bei großen Aufgaben phasenweise arbeiten.
- Rückfragen nur bei wirklich fehlenden Informationen stellen.
- Offene Punkte in `TASKS.md` dokumentieren.

## MagguuUI pack/copy product facts (pointer)

Dashboard stays HA-focused and does not invent MagguuUI Lua rules. When Stack updates Website/Bot WowUp starter/optional packs, Ellesmere TOC, or related product facts (no KSL/WindTools, etc.), reflect the same delta here in a short note so helpers do not drift across repos. Canonical detail lives in MagguuUI-Website / MagguuBot `AGENTS.md`.

- Current state (2026-10-12): MagguuUI addon live **v12.1.7**. The old whisper addon is fully removed everywhere; WowUp Optional includes **Whisper Messenger** (WhisperMessenger) as the whisper chat. The in-game player button is called **„Apply Magguu profiles“**.
- Node 24 / engines `>=24.17` applies to Website/Bot only (Node 26 locked until Marco says yes); this repo has no `package.json` / npm.

## Dependabot / Merge reports: Actions-only vs App-Image

Dashboard is HA YAML (+ `validate.yml` CI). There is **no** MagguuUI / MagguuBot Unraid image pull from this repo.

- **Actions-only** (github-actions pins, validate workflow, pip `requirements-dev.txt` for CI, docs) → squash-merge when CI green; **no Reviewer** needed; Buddy report: **Actions-only**; Homelab: none.
- **App-Image / Major** → normally N/A here (no Docker publish / no Magguu container rebuild). If a PR ever touched an App-Image path (it should not), do **not** merge without Reviewer Ship first.

CI/Security setup (2026-10-12): `validate.yml` runs on push and PR. Dependabot covers github-actions + pip (grouped, Monday Europe/Berlin). No npm ecosystem unless a `package.json` is added. Planned, not live yet: CodeQL (python + actions, SHA-pinned like MagguuBot) and a weekly `validate.yml` schedule (`17 4 * * 1`).

Merge reports must say **Actions-only vs App-Image** (expect **Actions-only**).
